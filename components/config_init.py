import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import sys
sys.path.append(r"C:\Users\Вадим\Documents\python\trade-brain-main")
import config
from components import transform_file

def setup_edge_driver():
    """Настраивает и возвращает драйвер Edge"""
    edge_options = Options()
    edge_options.add_argument("--log-level=3")  # Уровень логирования: 0=INFO, 1=WARNING, 2=ERROR, 3=FATAL
    edge_options.add_argument("--disable-logging")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # Создаем сервис и драйвер Edge
    service = Service()
    driver = webdriver.Edge(service=service, options=edge_options)
    return driver

def accept_cookies_if_present(driver):
    """Проверяет и принимает cookies соглашение"""
    try:

        # Ждем немного для появления окна
        time.sleep(3)

        # Ищем все кликабельные элементы
        cookie_buttons = driver.find_elements(By.CSS_SELECTOR, "button, a, div, span, input[type='button'], input[type='submit']")

        for button in cookie_buttons:
            try:
                text = button.text.strip().lower()
                if 'принять' in text or 'accept' in text or 'согласен' in text or 'agree' in text:
                    button.click()
                    return True
            except:
                continue
        return False

    except Exception as e:
        return False

def accept_user_agreement_if_present(driver):
    """Проверяет и принимает пользовательское соглашение"""
    try:
        # Ищем кнопку "Согласен" или аналогичную
        try:
            agree_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Согласен') or contains(text(), 'Согласиться') or contains(text(), 'Принимаю') or contains(text(), 'Accept') or contains(text(), 'Agree')]")
            for element in agree_elements:
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    return True
        except:
            pass
        time.sleep(2)
        return False

    except Exception as e:
        return False

def save_all_text_with_tables(driver, url, filename, ticker):
    """Сохранение всего текста с таблицами в файл"""
    try:
        # Получаем HTML страницы
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        # Удаляем скрипты и стили
        for script in soup(["script", "style", "meta", "link", "noscript"]):
            script.decompose()

        # Собираем текст
        all_text = []

        # Получаем основной текст
        main_text = soup.get_text(separator='\n', strip=True)
        all_text.append(main_text)

        # Получаем все таблицы
        tables = soup.find_all('table')
        if tables:

            for i, table in enumerate(tables, 1):

                # Парсим строки таблицы
                rows = table.find_all(['tr', 'th'])
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_text = []
                    for cell in cells:
                        cell_text = cell.get_text(strip=True)
                        if cell_text:
                            row_text.append(cell_text)

                    if row_text:
                        # Соединяем ячейки через табуляцию для лучшей читаемости
                        all_text.append("\t".join(row_text))
        with open(filename, 'w', encoding='utf-8') as file:
            file.write("\n".join(all_text))

        with open(filename, 'r', encoding='utf-8') as f:
            text = f.readlines()
            with open('C:/QUIK_DATA/config_init_content.txt', 'a') as file:
                for i in range(len(text)):
                    if text[i][:-1] =='Шаг цены':
                        STEP = text[i+1][:-1]
                    if text[i][:-1] =='Стоимость шага цены':
                        PRICE_STEP = text[i+1][:-1]
                    if text[i][:-1]== 'КОУР':
                        GO = text[i+1][:-1]
                        file.write(f'{ticker}:{STEP}/{PRICE_STEP}/{GO}\n')
                        with open(filename, 'w', encoding='utf-8') as file:
                            file.write("")
                        break

        return True

    except Exception as e:
        return False

def config_main():
    with open('C:/QUIK_DATA/config_init_content.txt', 'w') as file:
        file.write('')
    try:
        tickers = []
        for i in config.TRADING_TIKERS:
            tickers.append(config.TRADING_TIKERS[i])

        driver = setup_edge_driver() # Настраиваем драйвер
        time.sleep(7)
        driver.get(f'https://www.moex.com/ru/contract.aspx?code={tickers[0]}')
        accept_user_agreement_if_present(driver) # Принимаем пользовательское соглашение

        for i in tickers:
            url = f'https://www.moex.com/ru/contract.aspx?code={i}'
            # Ждем полной загрузки
            time.sleep(3)
            filename = "C:/QUIK_DATA/cache.txt"
            save_all_text_with_tables(driver, url, filename, i)
            driver.get(url)
        driver.quit()
        with open('C:/QUIK_DATA/config_init_content.txt', 'r') as file:
            content = file.readlines()
        config.INSTRUMENTS = transform_file.transform_file_to_dict(content)
    except:
        pass

if __name__ == "__main__":
    config_main()