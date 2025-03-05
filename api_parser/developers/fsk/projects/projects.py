import logging
import requests
import pandas as pd

# Инициализация логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def flatten_json(nested_json, parent_key='', sep='_'):
    """
    Рекурсивное "разворачивание" JSON в плоскую структуру.
    Возвращает словарь, где вложенные ключи "склеены" через sep.
    """
    items = []
    for k, v in nested_json.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            # Если список состоит только из словарей, разворачиваем каждый
            if all(isinstance(i, dict) for i in v):
                for idx, i in enumerate(v):
                    items.extend(flatten_json(i, f"{new_key}_{idx}", sep=sep).items())
            else:
                # Если в списке не словари, объединяем значения в одну строку
                items.append((new_key, ', '.join(map(str, v))))
        else:
            items.append((new_key, v))
    return dict(items)


def process_json_list(json_list):
    """
    Обрабатывает список JSON-объектов, разворачивая вложенные структуры
    и формируя несколько записей из одного объекта, если есть ключ 'travel'.
    """
    processed_data = []
    for item in json_list:
        # Основные данные (без учёта 'travel')
        base_data = flatten_json(item)

        # Если есть вложенный список 'travel', делаем отдельные записи
        if 'travel' in item and isinstance(item['travel'], list):
            for travel_item in item['travel']:
                travel_data = flatten_json(travel_item, 'travel')
                merged_data = {**base_data, **travel_data}
                processed_data.append(merged_data)
        else:
            processed_data.append(base_data)

    return processed_data


def main():
    """
    Основная функция:
    1. Выполняет запрос к API.
    2. Выводит базовую информацию и проверяет структуру ответа.
    3. Разворачивает данные и сохраняет в CSV.
    """
    session = requests.Session()
    response = session.get('https://fsk.ru/api/v3/projects/all')

    if response.status_code == 200:
        all_projects = response.json()

        # Логируем структуру данных
        logger.info(f"Тип данных all_projects: {type(all_projects)}")
        if isinstance(all_projects, list):
            logger.info(f"Количество проектов: {len(all_projects)}")
        else:
            logger.warning("Ошибка: API вернуло неожиданный формат данных.")

        # Обрабатываем JSON
        processed_projects = process_json_list(all_projects)

        # Превращаем в DataFrame
        df = pd.DataFrame(processed_projects)
        logger.info(f"Форма DataFrame: {df.shape}")

        # Сохраняем в CSV
        csv_filename = "projects_expanded.csv"
        df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
        logger.info(f"Файл сохранён как {csv_filename}")
    else:
        logger.error(f"Ошибка запроса API: {response.status_code}")


if __name__ == "__main__":
    main()
