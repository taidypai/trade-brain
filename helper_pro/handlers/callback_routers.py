import os
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
import keyboards

callback_router = Router()

# Глобальное хранилище для ID стартовых сообщений
start_message_ids = {}

# Состояния для FSM
class LevelStates(StatesGroup):
    waiting_for_level_price = State()
    waiting_for_level_stop_loss = State()

class DealStates(StatesGroup):
    waiting_for_stop_loss = State()


async def edit_start_message(bot, user_id: int, text: str, reply_markup=None):
    """Редактирование стартового сообщения"""
    try:
        message_id = start_message_ids.get(user_id)
        if message_id:
            await bot.edit_message_text(
                chat_id=user_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"Error editing start message: {e}")

# Основное меню
@callback_router.callback_query(F.data == "back_to_main")
async def handle_back_to_main(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await asyncio.sleep(3)
    await edit_start_message(
        callback.bot,
        callback.from_user.id,
        "Добро пожаловать в экосистему *Trade & Brain!*",
        keyboards.main_keyboard()
    )
    await state.clear()
    await callback.answer()


# Торговые пары
@callback_router.callback_query(F.data.startswith("pair_"))
async def handle_pair_selection(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора торговой пары"""
    try:
        pair = callback.data.replace("pair_", "")
        await state.update_data(selected_pair=pair)
        await state.set_state(DealStates.waiting_for_stop_loss)

        await edit_start_message(
            callback.bot,
            callback.from_user.id,
            f"Введите стоп-лосс для {pair}:",
            keyboards.back_to_main_keyboard()
        )
        await callback.answer()

    except Exception as e:
        print(f"Error in pair selection: {e}")
        await callback.answer("Произошла ошибка")

@callback_router.message(DealStates.waiting_for_stop_loss)
async def handle_stop_loss_input(message: Message, state: FSMContext):
    """Обработка ввода стоп-лосса"""
    try:
        stop_loss = message.text.strip()

        # Проверяем, что введено число
        try:
            stop_loss_value = float(stop_loss)
        except ValueError:
            await message.delete()
            await edit_start_message(
                message.bot,
                message.from_user.id,
                "Пожалуйста, введите корректное число для стоп-лосса:",
                keyboards.back_to_main_keyboard()
            )
            return
        # Получаем данные из состояния
        state_data = await state.get_data()
        selected_pair = state_data.get('selected_pair')

        # Записываем в файл executive.txt
        path = "C:/QUIK_DATA/order_list.txt"
        try:
            with open(path, "a", encoding="utf-8") as file:
                file.write(f"{selected_pair}:{stop_loss}")
        except Exception as e:
            print(f"Error writing to file: {e}")
            await edit_start_message(
                message.bot,
                message.from_user.id,
                "Ошибка записи в файл",
                keyboards.main_keyboard()
            )
            return

        # Удаляем сообщение пользователя
        await message.delete()
        await asyncio.sleep(10)
        # Показываем временное сообщение об исполнении
        # Удаляем временное сообщение

        # Возвращаем главное меню
        await edit_start_message(
            message.bot,
            message.from_user.id,
            "Добро пожаловать в экосистему *Trade & Brain!*",
            keyboards.main_keyboard()
        )

        await state.clear()

    except Exception as e:
        print(f"Error in stop loss input: {e}")
        await edit_start_message(
            message.bot,
            message.from_user.id,
            "Произошла ошибка при обработке стоп-лосса",
            keyboards.main_keyboard()
        )