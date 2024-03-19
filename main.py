import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers import main_menu, registration
from functions import manage_google_sheets
from logger import logger


async def main():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    load_dotenv()
    dp = Dispatcher()
    dp.include_router(main_menu.start_router)
    dp.include_router(registration.registration_router)
    logger.info("Starting bot ...")
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(manage_google_sheets(), dp.start_polling(bot))


if __name__ == "__main__":
    asyncio.run(main())
