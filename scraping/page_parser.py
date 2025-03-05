# page_parser.py
import time
import logging
from selenium.webdriver.common.by import By
from driver import create_driver
from card_parser import process_card

def process_page(page_num):
    """
      Создает драйвер и открывает страницу с карточками
      Собирает ссылки на карточки
      Для каждой карточки вызывает process_card для получения данных
      Закрывает драйвер и возвращает список данных с этой страницы
    """
    
    page_url = f"https://realty.yandex.ru/moskva_i_moskovskaya_oblast/kupit/kvartira/novostroyki/?page={page_num}"
    logging.info(f"Обрабатываем страницу {page_num}: {page_url}")
    
    drv = create_driver()
    drv.get(page_url)
    time.sleep(2)
    
    cards = drv.find_elements(By.CSS_SELECTOR, '[data-test="OffersSerpItem"]')
    card_urls = []
    for c in cards:
        try:
            a_el = c.find_element(By.CSS_SELECTOR, "a")
            link = a_el.get_attribute("href")
            card_urls.append(link)
        except Exception as e:
            logging.error(f"Ошибка получения ссылки карточки: {e}")
    drv.quit()
    
    pages = []
    total = len(card_urls)
    for idx, url in enumerate(card_urls, start=1):
        data = process_card(url, idx, total)
        if data:
            pages.append(data)
    return pages
