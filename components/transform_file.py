# Самый простой и рабочий вариант:
def transform_file_to_dict(data_lines):
    instruments = {}

    for line in data_lines:
        try:
            line = line.strip()
            if not line:
                continue

            # Разделяем тикер и остальное
            ticker, rest = line.split(':', 1)
            ticker = ticker.strip()

            # Убираем пробел между числами в конце: "6 869.93" -> "6869.93"
            # Ищем последний пробел между цифрами
            import re
            # Паттерн: число, пробел, число с точкой
            match = re.search(r'(\d+)\s+(\d+\.\d+)$', rest)
            if match:
                # Заменяем пробел на пустоту
                num1, num2 = match.groups()
                rest = rest.replace(f"{num1} {num2}", f"{num1}{num2}")

            # Теперь разделяем
            step_str, step_cost_str, lot_price_str = rest.split('/')

            # Конвертируем
            step = float(step_str.strip().replace(',', '.'))
            step_cost = float(step_cost_str.strip().replace(',', '.'))
            lot_price = float(lot_price_str.strip().replace(',', '.'))

            instruments[ticker] = {
                'step': step,
                'step_cost': step_cost,
                'lot_price': lot_price
            }

        except Exception as e:
            print(f"Ошибка в строке '{line}': {e}")
            continue

    return instruments


# Тестируем
if __name__ == "__main__":
    data_lines = [
        'IMOEXF:0,5/5/6 869.93',
        'GLDRUBF:0,5/5/6 869.93',
        'NAZ5:0,1/0,1/2 694.44',
        'VBZ5:1/0,77703/5 841.68'
    ]

    result = transform_file_to_dict_fixed(data_lines)

    print("Результат:")
    for ticker, data in result.items():
        print(f"{ticker}: step={data['step']}, step_cost={data['step_cost']}, lot_price={data['lot_price']}")