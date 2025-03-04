import requests
import json
import pandas as pd

# Функция для рекурсивного "разворачивания" JSON в плоскую структуру
def flatten_json(nested_json, parent_key='', sep='_'):
    items = []
    for k, v in nested_json.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_json(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            if all(isinstance(i, dict) for i in v):  # Если список словарей
                for idx, i in enumerate(v):
                    items.extend(flatten_json(i, f"{new_key}_{idx}", sep=sep).items())
            else:
                items.append((new_key, ', '.join(map(str, v))))  # Объединяем список значений в строку
        else:
            items.append((new_key, v))
    return dict(items)

# Функция для обработки JSON и создания нескольких записей
def process_json_list(json_list):
    processed_data = []
    for item in json_list:
        base_data = flatten_json(item)  # Основные данные проекта без вложенных списков

        # Обрабатываем вложенный список travel
        if 'travel' in item:
            for travel_item in item['travel']:
                travel_data = flatten_json(travel_item, 'travel')  # Разворачиваем travel
                merged_data = {**base_data, **travel_data}  # Объединяем данные
                processed_data.append(merged_data)
        else:
            processed_data.append(base_data)  # Если travel нет, просто добавляем основной объект

    return processed_data

# Запрос API
session = requests.Session()
response = session.get('https://fsk.ru/api/v3/projects/all')

if response.status_code == 200:
    all_projects = response.json()  # Загружаем JSON

    # Проверим структуру данных
    print(f"Тип данных all_projects: {type(all_projects)}")  
    if isinstance(all_projects, list):
        print(f"Количество проектов: {len(all_projects)}")
        print(f"Пример одного проекта: {json.dumps(all_projects[0], indent=2, ensure_ascii=False)}")
    else:
        print("Ошибка: API вернуло неожиданный формат данных.")

    # Обрабатываем JSON
    processed_projects = process_json_list(all_projects)

    # Конвертируем в DataFrame
    df = pd.DataFrame(processed_projects)

    # Проверяем, получилось ли что-то
    print(f"Форма DataFrame: {df.shape}")
    print(df.head())

    # Сохраняем в CSV
    csv_filename = "projects_expanded.csv"
    df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
    print(f"Файл сохранён как {csv_filename}")
else:
    print(f"Ошибка запроса API: {response.status_code}")
