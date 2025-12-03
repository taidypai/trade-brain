# C:\Users\Вадим\Documents\python\trade-brain-main
from components import start_quik, setup_environment
from components.time_service import timeservice
from liquidity_process import liquid_main
from impuls_process import impuls_main
from trading_engine import trade_main
from components.start_quik import launcher_quik
from components import config_init
from helper_pro import run_bot
import config
import asyncio
import datetime
import time
import signal
import sys
import os

async def run_all_processes():
    """Запускает все торговые процессы параллельно"""
    print(" === Trade & Brain === ")
    print('/-- Автоматическая настройка пространства. loading...')

    # Инициализация компонентов
    start_quik.quik_main()  # Запуск QUIK
    setup_environment.environment_main()  # Настройка директорий
    config_init.config_main()

    # Запускаем все процессы параллельно
    tasks = [
        asyncio.create_task(liquid_main.liquidity_main(), name="liquidity"),
        asyncio.create_task(impuls_main.impuls_main(), name="impuls"),
        asyncio.create_task(trade_main.trade_main(), name="trading")
    ]

    # Бесконечно ждем (до прерывания пользователем)
    await asyncio.gather(*tasks)

async def check_and_restart_time():
    """
    Проверяет, не 8:50 ли утра, и если да - перезапускает программу
    """
    while True:
        now = datetime.datetime.now()

        # Проверяем, 8:50 утра
        if now.hour == 8 and now.minute == 50:
            print(f"\n{'='*60}")
            print(f"Время перезапуска: {now.strftime('%H:%M:%S')}")
            print("Обнаружено время 8:50 - выполняю перезапуск всех задач...")
            print(f"{'='*60}\n")

            # Перезапускаем программу
            restart_program()

        # Ждем 1 минуту до следующей проверки
        await asyncio.sleep(60)

def restart_program():
    """
    Перезапускает текущую программу
    """
    print("Завершаю текущие процессы и перезапускаю...")

    # Завершаем программу и перезапускаем
    python = sys.executable
    os.execl(python, python, *sys.argv)

async def main_with_scheduler():
    """
    Основная функция с планировщиком перезапуска
    """
    # Запускаем проверку времени в фоновой задаче
    scheduler_task = asyncio.create_task(check_and_restart_time(), name="scheduler")

    # Запускаем основные процессы
    processes_task = asyncio.create_task(run_all_processes(), name="processes")

    # Ожидаем завершения любой из задач
    await asyncio.wait([scheduler_task, processes_task], return_when=asyncio.FIRST_COMPLETED)

    # Если одна задача завершилась, отменяем другую
    scheduler_task.cancel()
    processes_task.cancel()

    # Ждем корректного завершения
    try:
        await scheduler_task
    except asyncio.CancelledError:
        pass

    try:
        await processes_task
    except asyncio.CancelledError:
        pass

def init_main():
    # Получаем текущее время для отладки
    now = datetime.datetime.now()
    print(f"Текущее время: {now.strftime('%H:%M:%S')}")
    print(f"Перезапуск будет выполнен в 8:50 утра\n")

    # Запускаем основную функцию с планировщиком
    asyncio.run(main_with_scheduler())

if __name__ == "__main__":
    init_main()
