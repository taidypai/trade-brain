# liquid_main.py C:\Users\Вадим\Documents\python\trade-brain-main\trading_engine
import sys
sys.path.append(r"C:\Users\Вадим\Documents\python\trade-brain-main")
from components.send_telegram_message import send_tg_message
from trading_engine.louncher import Louncher_trade_engine, monitoring_orders
import asyncio

async def trade_main():
    """Асинхронная главная функция"""
    while True:
        line = monitoring_orders()
        if line:
            parts = line.split(':')
            pair = parts[0]      # 'GLDRUBF'
            stop_loss = parts[1]
            print(parts[1])
            print(parts) # '1045.4'

            # Создаем экземпляр и запускаем стратегию
            trade_engine = Louncher_trade_engine(pair, stop_loss)

            # Запускаем асинхронную стратегию с await
            success = await trade_engine.execute_trading_strategy()

            if success:
                send_tg_message(f'Сделка успешно завершена прибыль: +{trade_engine.take} ₽')


        await asyncio.sleep(1)


if __name__ == "__main__":
    # Запускаем асинхронную main функцию
    asyncio.run(trade_main())