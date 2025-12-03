from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import sys
sys.path.append(r"C:\Users\Вадим\Documents\python\trade-brain-main")
import config
def main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Кнопка "Trade & Brain" - отдельно
    builder.row(
        InlineKeyboardButton(text="Trade & Brain", url="t.me/trade_and_brain"),
    )

    # Берем все пары из TRADING_TIKERS
    tickers = list(config.TRADING_TIKERS.items())

    # Создаем кнопки парами (по 2 в ряд)
    for i in range(0, len(tickers), 2):
        if i + 1 < len(tickers):
            # Есть пара кнопок для ряда
            ticker1_text, ticker1_code = tickers[i]
            ticker2_text, ticker2_code = tickers[i + 1]

            builder.row(
                InlineKeyboardButton(text=ticker1_text, callback_data=f"pair_{ticker1_text}"),
                InlineKeyboardButton(text=ticker2_text, callback_data=f"pair_{ticker2_text}")
            )
        else:
            # Последняя нечетная кнопка
            ticker_text, ticker_code = tickers[i]
            builder.row(
                InlineKeyboardButton(text=ticker_text, callback_data=f"pair_{ticker_text}")
            )

    return builder.as_markup()

def back_to_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Главное меню", callback_data="back_to_main"),
    )
    return builder.as_markup()

# Добавь этот метод если хочешь использовать main_menu_keyboard()
def main_menu_keyboard() -> InlineKeyboardMarkup:
    return main_keyboard()