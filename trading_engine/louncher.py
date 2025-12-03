import asyncio
import sys

sys.path.append(r"C:\Users\Вадим\Documents\python\trade-brain-main")
import config
from components.send_telegram_message import send_tg_message
from components.get_price_action import get_price
from components.finam_balance import get_finam_balance  # Импортируем асинхронную функцию VTBR-12.25:7250.


class Louncher_trade_engine:
    def __init__(self, pair, stop_loss):
        self.PERCENT_RISK = 0.02
        self.INSTRUMENTS = config.INSTRUMENTS
        self.pair = config.TRADING_TIKERS[pair]
        self.ticker = pair
        self.start_price = float(get_price()[self.ticker])
        self.stop_loss = float(stop_loss)
        self.balance = None
        self.QUANTITY = None
        self.order_quantity_1 = None
        self.order_quantity_2 = None
        self.take = 0

    async def initialize(self):
        """Асинхронная инициализация баланса и расчетов"""
        self.balance = await get_finam_balance()

        # Рассчитываем максимальное количество лотов
        MAX_LOTS = self.balance // self.INSTRUMENTS[self.pair]['lot_price']
        # Рассчитываем количество для торговли
        price_diff = self.start_price - self.stop_loss
        steps = price_diff / self.INSTRUMENTS[self.pair]['step']
        risk_per_lot = steps * self.INSTRUMENTS[self.pair]['step_cost']
        risk_amount = self.balance * self.PERCENT_RISK

        self.QUANTITY = int(risk_amount // risk_per_lot) if risk_per_lot > 0 else 1
        # Проверяем ограничения по количеству
        if self.QUANTITY > MAX_LOTS:
            self.QUANTITY = int(MAX_LOTS)
        elif self.QUANTITY < 1:
            self.QUANTITY = 1

        # Разделяем количество на две части
        if self.QUANTITY % 2 == 0:
            self.order_quantity_1 = int(self.QUANTITY / 2)
            self.order_quantity_2 = self.order_quantity_1
        else:
            self.order_quantity_1 = int(self.QUANTITY // 2 + 1)
            self.order_quantity_2 = int(self.QUANTITY - self.order_quantity_1)

        # Создаем начальный ордер на покупку
        self.create_order(self.pair, 'B', self.QUANTITY)
        self.take_profit_1 = self.start_price + abs((self.start_price - self.stop_loss) * 2)
        self.take_profit_2 = self.start_price + abs((self.start_price - self.stop_loss) * 2.5)
        send_tg_message(f'Количество лотов: {self.QUANTITY} \nStopLoss {self.stop_loss}\nTakeProfit 1 {self.take_profit_1}\nTakeProfit 2 {self.take_profit_2}')

    async def execute_trading_strategy(self):
        """Асинхронная торговая стратегия"""
        # Инициализируем баланс и расчеты
        await self.initialize()
        while True:  # Первый уровень
            current_price = float(get_price()[self.ticker])
            if current_price >= self.take_profit_1:
                self.create_order(self.pair, 'S', self.order_quantity_1)
                profit_1 = (((current_price - self.start_price) / (self.INSTRUMENTS[self.pair]['step'])) * self.INSTRUMENTS[self.pair]['step_cost'] * self.order_quantity_1)
                send_tg_message(f'Level 1 TakeProfit +{profit_1:.2f}')

                # Второй уровень
                while True:
                    current_price_2 = float(get_price()[self.ticker])

                    # Take Profit 2
                    take_profit_2 = self.start_price + abs((self.start_price - self.stop_loss) * 2.5)

                    if current_price_2 >= self.take_profit_2:
                        self.create_order(self.pair, 'S', self.order_quantity_2)
                        profit_2 = (((current_price - self.start_price) / (self.INSTRUMENTS[self.pair]['step'])) * self.INSTRUMENTS[self.pair]['step_cost'] * self.order_quantity_2)
                        send_tg_message(f'Level 2 Сработал TakeProfit + {profit_2}')
                        self.take = profit_2 + profit_1
                        return True

                    # Stop Loss 2
                    elif current_price_2 <= self.stop_loss:
                        self.create_order(self.pair, 'S', self.order_quantity_2)
                        if self.QUANTITY % 2 == 0:
                            send_tg_message('Level 2 Сработал Stoploss 0')
                        else:
                            # Для нечетного количества первый ордер уже в плюсе
                            loss_2 = ((current_price_2 - self.start_price) / self.INSTRUMENTS[self.pair]['step']) * self.INSTRUMENTS[self.pair]['step_cost'] * self.order_quantity_2
                            total = profit_1_final + loss_2
                            send_tg_message(f'Level 2 Сработал Stoploss 0')
                        return True
                    await asyncio.sleep(1)

            # Stop Loss 1 (полная позиция)
            elif current_price <= self.stop_loss:
                self.create_order(self.pair, 'S', self.QUANTITY)
                loss = ((current_price - self.start_price) / self.INSTRUMENTS[self.pair]['step']) * self.INSTRUMENTS[self.pair]['step_cost'] * self.QUANTITY
                send_tg_message(f'Level 1 Сработал Stoploss -{abs(loss):.2f}')
                return True

            await asyncio.sleep(1)

    def create_order(self, ticker, operation, quantity):
        """Создание ордера"""
        if quantity > 0:
            with open('C:/QUIK_DATA/order.txt', 'w') as file:
                file.write(f'DEAL:{ticker}/{operation}/{quantity}')

def monitoring_orders():
    """Мониторинг новых ордеров"""
    try:
        with open('C:/QUIK_DATA/order_list.txt', 'r') as file:
            content = file.read().strip()
            if content != '':
                # Очищаем файл после чтения
                with open('C:/QUIK_DATA/order_list.txt', 'w') as file:
                    file.write('')
                return content
            else:
                return False
    except FileNotFoundError:
        print("Файл order_list.txt не найден")
        return False
    except Exception as e:
        print(f"Ошибка при чтении ордеров: {e}")
        return False