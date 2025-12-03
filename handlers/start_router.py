import logging
from aiogram.filters import Command, CommandStart
from aiogram import types, Router
import asyncio

import keyboards
from handlers.callback_routers import start_message_ids

logger = logging.getLogger(__name__)
start_router = Router()

@start_router.message(CommandStart())
async def handle_start(message: types.Message):
    """Обработка команды /start"""
    try:
        welcome_text = "Добро пожаловать в экосистему *Trade & Brain*!"

        # Отправляем стартовое сообщение и сохраняем его ID
        start_message = await message.answer(
            welcome_text,
            reply_markup=keyboards.main_keyboard(),
            parse_mode='Markdown'
        )

        # Сохраняем ID стартового сообщения
        start_message_ids[message.from_user.id] = start_message.message_id

    except Exception as e:
        logger.error(f"Error in start handler: {e}")
        await message.answer("Произошла ошибка при запуске бота")