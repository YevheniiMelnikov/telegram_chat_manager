import asyncio

from google.oauth2.service_account import Credentials
from gspread_asyncio import AsyncioGspreadClientManager

from bot.models import Event
from logger import logger
from settings import EVENTS_DATA_TTL
from storage import Storage
from utils import singleton


@singleton
class GoogleSheetsManager:
    def __init__(self, spreadsheet_id: str, credentials_file: str, storage: Storage):
        self.spreadsheet_id = spreadsheet_id
        self.client_manager = AsyncioGspreadClientManager(
            credentials_fn=lambda: self.load_credentials(credentials_file)
        )
        self.storage = storage
        self.client = None
        self.spreadsheet = None

    async def get_spreadsheet(self):
        self.client = await self.client_manager.authorize()
        spreadsheet = await self.client.open_by_key(self.spreadsheet_id)
        self.spreadsheet = await spreadsheet.get_sheet1()

    @staticmethod
    def load_credentials(credentials_file: str) -> Credentials:
        creds = None
        if credentials_file:
            creds = Credentials.from_service_account_file(
                credentials_file,
                scopes=[
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/spreadsheets",
                    "https://www.googleapis.com/auth/drive",
                ],
            )
        return creds

    async def get_events(self) -> list[Event]:
        await self.get_spreadsheet()

        name_list, date_list, time_list, address_list, price_list, description_list = await asyncio.gather(
            self.get_name_list(),
            self.get_date_list(),
            self.get_time_list(),
            self.get_address_list(),
            self.get_price_list(),
            self.get_description_list(),
        )

        return [
            Event(
                id=id_,
                name=name,
                date=date,
                time=time,
                address=address,
                price=price,
                description=description,
            )
            for id_, name, date, time, address, price, description in zip(
                range(1, len(name_list) + 1),
                name_list,
                date_list,
                time_list,
                address_list,
                price_list,
                description_list,
            )
        ]

    async def get_name_list(self) -> list[str]:
        cells = await self.spreadsheet.get("A2:A")
        return [cell for row in cells for cell in row]

    async def get_date_list(self) -> list[str]:
        cells = await self.spreadsheet.get("B2:B")
        return [cell for row in cells for cell in row]

    async def get_time_list(self) -> list[str]:
        cells = await self.spreadsheet.get("C2:C")
        return [cell for row in cells for cell in row]

    async def get_price_list(self) -> list[float | None]:
        cells = await self.spreadsheet.get("D2:D")
        return [cell if cell != "-" else None for row in cells for cell in row]

    async def get_description_list(self) -> list[str]:
        cells = await self.spreadsheet.get("F2:F")
        return [cell for row in cells for cell in row]

    async def get_address_list(self) -> list[str]:
        cells = await self.spreadsheet.get("G2:G")
        return [cell for row in cells for cell in row]

    async def run(self) -> None:
        try:
            await self.storage.update_events(await self.get_events())
            while True:
                await asyncio.sleep(EVENTS_DATA_TTL)
                await self.storage.update_events(await self.get_events())
                logger.info(f"Data fetched from Google Sheets")
        except Exception as e:
            logger.error(f"Error while updating Google Sheets: {e}")
