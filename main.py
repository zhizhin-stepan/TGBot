import asyncio 
from aiogram import Bot, Dispatcher

from app.handlers import router


async def main():
    bot = Bot(token='8190560831:AAF60-YY-lJc6L_nm2nQ8Gsee4TaLaQVoWk')
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен!')