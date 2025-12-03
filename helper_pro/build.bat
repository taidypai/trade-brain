@echo off
chcp 65001
echo Сборка Telegram бота...

:: Создаем виртуальное окружение
python -m venv bot_venv
call bot_venv\Scripts\activate.bat

:: Устанавливаем зависимости
pip install aiogram aiofiles pyinstaller

:: Собираем в exe
pyinstaller --onefile --name "TelegramTradeBot" --hidden-import=aiogram --hidden-import=aiogram.filters --hidden-import=aiogram.types --hidden-import=handlers.start_router --hidden-import=handlers.message_router --hidden-import=handlers.callback_routers run_bot.py

echo.
echo ============================================
echo Сборка завершена!
echo Исполняемый файл: dist\TelegramTradeBot.exe
echo ============================================
pause