import asyncio 
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from app.handlers import router
from aiogram.fsm.storage.memory import MemoryStorage
from fill_database import check_database, update_database


async def database_precheck():
    # Проверка и обновление БД перед запуском
    if not check_database():
        print("Обнаружены расхождения в данных, начинаю обновление...")
        if update_database():
            print("База данных успешно обновлена!")
        else:
            print("Не удалось обновить базу данных!")

async def main():
    await database_precheck()

    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=storage)
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен!')