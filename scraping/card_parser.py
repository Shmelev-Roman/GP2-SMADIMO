# card_parser.py
import time
import brotli
import json
import logging
from seleniumwire import webdriver

def process_card(card_url, idx, total):
    """
      Создает новый драйвер и открывает URL карточки
      Ждет 3 секунды для загрузки страницы и отправки запросов
      Перебирает все запросы, ищет endpoint map-nearby-suggestions
      сли запрос найден, декомпрессирует и парсит ответ, извлекая нужные данные
      Закрывает драйвер и возвращает словарь с данными
    """
    logging.info(f"Обрабатываем карточку {idx}/{total}: {card_url}")
    opt = webdriver.Chromeopt()
    opt.add_argument("--headless")
    opt.add_argument("disable-logging")
    drv = webdriver.Chrome(seleniumwire_opt={}, opt=opt)
    card_data = None
    try:
        drv.get(card_url)
        time.sleep(3)  # ждем загрузки страницы и прихода запросов
        
        for req in drv.requests:
            if req.response and "map-nearby-suggestions" in req.url:
                body = req.response.body
                try:
                    dc = brotli.decompress(body)
                except Exception as e:
                    logging.error(f"Ошибка декомпрессии для карточки {card_url}: {e}")
                    dc = body
                try:
                    data_str = dc.decode('utf-8')
                except Exception as e:
                    logging.error(f"Ошибка декодирования для карточки {card_url}: {e}")
                    data_str = ""
                try:
                    js = json.loads(data_str)
                except Exception as e:
                    logging.error(f"Ошибка загрузки JSON для карточки {card_url}: {e}")
                    js = None
                if js:
                    try:
                        itm = js["response"]["points"][0]["item"]
                        card_data = {
                            "offerId": itm.get("offerId", ""),
                            "developer": itm.get("salesDepartments", [{}])[0].get("name", ""),
                            "area": itm.get("area", {}).get("value"),
                            "livingArea": itm.get("livingSpace", {}).get("value"),
                            "rooms": itm.get("roomsTotal"),
                            "floor": itm.get("floorsOffered", [None])[0],
                            "floorsTotal": itm.get("floorsTotal"),
                            "price": itm.get("price", {}).get("value"),
                            "pricePerM2": itm.get("price", {}).get("valuePerPart"),
                            "yearBuilt": itm.get("building", {}).get("builtYear"),
                            "quarterBuilt": itm.get("building", {}).get("builtQuarter"),
                            "buildingType": itm.get("building", {}).get("buildingType", ""),
                            "parking": itm.get("building", {}).get("improvements", {}).get("PARKING", False),
                            "lift": itm.get("building", {}).get("improvements", {}).get("LIFT", False),
                            "security": itm.get("building", {}).get("improvements", {}).get("SECURITY", False),
                            "address": itm.get("location", {}).get("geocoderAddress", ""),
                            "latitude": itm.get("location", {}).get("point", {}).get("latitude"),
                            "longitude": itm.get("location", {}).get("point", {}).get("longitude"),
                            "metroName": itm.get("location", {}).get("metro", {}).get("name"),
                            "metroTime": itm.get("location", {}).get("metro", {}).get("timeToMetro"),
                            "metroTransport": itm.get("location", {}).get("metro", {}).get("metroTransport"),
                            "parksCount": len(itm.get("location", {}).get("parks", [])),
                            "pondsCount": len(itm.get("location", {}).get("ponds", [])),
                            "metroStationsCount": len(itm.get("location", {}).get("metroList", [])),
                            "hasPriceHistory": itm.get("price", {}).get("hasPriceHistory", False),
                            "pricePrev": itm.get("price", {}).get("previous"),
                            "profitabilityDesc": next((h.get("description") for h in itm.get("location", {}).get("allHeatmaps", []) if h.get("name") == "profitability"), None),
                            "profitabilityLevel": next((h.get("level") for h in itm.get("location", {}).get("allHeatmaps", []) if h.get("name") == "profitability"), None)
                        }
                    except Exception as e:
                        logging.error(f"Ошибка извлечения данных из JSON для карточки {card_url}: {e}")
                break
    finally:
        drv.quit()
    if card_data:
        logging.info(f"Спарсены данные карточки {idx}: {card_data}")
    else:
        logging.info(f"Карточка {idx} не вернула данные.")
    return card_data
