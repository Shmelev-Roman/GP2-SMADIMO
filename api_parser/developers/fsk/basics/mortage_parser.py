import logging
import requests
import json
import pandas as pd
from pathlib import Path

from api_parser.data import config

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Создаём сессию requests
session = requests.Session()

# Словарь с путями, которые нужно запросить
paths = {
    'city': [
        '/'
    ],
    'mortgage': [
        '/'
    ],
    'banks': [
        '/'
    ],
    'v3/mortgage': [
        '/program/types'
    ],
}

# Указываем директорию для сохранения результатов
output_dir = Path('data')
# Создаём её, если не существует
output_dir.mkdir(exist_ok=True)

# Перебираем домены и пути для формирования полного URL
for domain in paths:
    for path in paths.get(domain):
        # Формируем URL для запроса
        url = config.FSK_API_URL + domain + path
        logger.info(f"Запрашиваем данные по адресу: {url}")

        try:
            response = session.get(url)
            response.raise_for_status()
            # Преобразуем ответ в JSON
            data = response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка при запросе к {url}: {e}")
            continue
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка декодирования JSON для {url}: {e}")
            continue

        # Преобразуем JSON в DataFrame
        df = pd.json_normalize(data)
        logger.info(f"Получено {len(df)} записей из {url}. Сохраняем в CSV.")

        # Формируем имя файла из domain и части пути
        path_name = (domain + path.split('/')[0] + '.csv').replace('/', '_')
        csv_path = output_dir / path_name

        # Сохраняем DataFrame в CSV
        df.to_csv(csv_path, index=False, encoding="utf-8-sig")
        logger.info(f"Файл сохранён: {csv_path}")
