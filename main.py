import asyncio

from aiogram import Bot, Dispatcher

from bot.handlers import main_menu, registration
from functions import manage_google_sheets
from logger import logger
from settings import BOT_TOKEN


async def main():
    bot = Bot(token=BOT_TOKEN)  # TODO: HIDE SENSITIVE DATA
    dp = Dispatcher()
    dp.include_router(main_menu.start_router)
    dp.include_router(registration.registration_router)
    logger.info("Starting bot ...")
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.gather(manage_google_sheets(), dp.start_polling(bot))


if __name__ == "__main__":
    asyncio.run(main())
