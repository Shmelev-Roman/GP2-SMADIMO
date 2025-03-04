import requests
import time
import pandas as pd

TIMEOUT = 10
RETRIES = 3

def safe_request(url):
    """Безопасный GET-запрос с повторными попытками."""
    for attempt in range(RETRIES):
        try:
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса {url}: {e} (попытка {attempt + 1}/{RETRIES})")
            time.sleep(2)
    return None

def flatten_json(nested_data, parent_key=""):
    """
    Рекурсивно «разворачивает» JSON-объект или список.
    Возвращает список словарей (строк), где каждая строка 
    содержит «дублированные» родительские поля и данные 
    из вложенного уровня.
    """
    # Если пришёл словарь, разбираем его ключи
    if isinstance(nested_data, dict):
        # Начинаем с одной «пустой» строки (словаря), которую будем расширять
        current_rows = [{}]
        
        for key, value in nested_data.items():
            # Формируем имя поля (учитываем, что у родителя может быть префикс)
            new_key = f"{parent_key}_{key}" if parent_key else key

            if isinstance(value, dict):
                # Разворачиваем вложенный словарь
                nested_rows = flatten_json(value, new_key)  # это список словарей

                # Для каждого already существующего row размножаем nested_rows
                updated_rows = []
                for row in current_rows:
                    for nrow in nested_rows:
                        # Склеиваем родительский row с каждой «дочерней» строкой
                        merged = {**row, **nrow}
                        updated_rows.append(merged)
                current_rows = updated_rows

            elif isinstance(value, list):
                # Если список словарей
                if all(isinstance(item, dict) for item in value):
                    updated_rows = []
                    for row in current_rows:
                        # Для каждого элемента списка делаем разворот
                        for item in value:
                            nested_rows = flatten_json(item, new_key)
                            for nrow in nested_rows:
                                merged = {**row, **nrow}
                                updated_rows.append(merged)
                    current_rows = updated_rows
                else:
                    # Если список несловари (числа, строки...) – 
                    # запихиваем их в одно поле
                    str_value = ", ".join(map(str, value))
                    for row in current_rows:
                        row[new_key] = str_value

            else:
                # Примитивное значение (строка, число и т.п.)
                for row in current_rows:
                    row[new_key] = value
        
        return current_rows

    # Если пришёл список "верхнего уровня" — обработаем каждый элемент как отдельную строку
    elif isinstance(nested_data, list):
        all_rows = []
        for item in nested_data:
            item_rows = flatten_json(item, parent_key)
            all_rows.extend(item_rows)
        return all_rows

    else:
        # Если вообще не словарь и не список (просто число/строка)
        return [{parent_key: nested_data}] if parent_key else [{'_value': nested_data}]


# -------------------------------------------
# Дальше идёт основная логика работы с API
# -------------------------------------------

# 1. Получаем список проектов
projects_url = 'https://fsk.ru/api/v3/projects/all'
projects_data = safe_request(projects_url)

if not projects_data:
    print("Не удалось получить список проектов. Завершаем работу.")
    exit()

# 2. Получаем slugs всех проектов
projects_slugs = [p.get('slug') for p in projects_data if p.get('slug')]

# 3. Сбор всех квартир в единый список (как в вашем коде)
all_flats_raw = []

for slug in projects_slugs:
    print(f"Обрабатываем проект: {slug}")
    first_page_url = f'https://fsk.ru/api/v3/flats/?order=asc&page=1&project_slug={slug}'
    first_page_data = safe_request(first_page_url)

    if not first_page_data:
        print(f"Пропускаем проект {slug} из-за ошибки запроса.")
        continue

    total_pages = first_page_data.get('totalPages', 1)
    all_flats_raw.extend(first_page_data.get('items', []))

    for page in range(2, total_pages + 1):
        page_url = f'https://fsk.ru/api/v3/flats/?order=asc&page={page}&project_slug={slug}'
        page_data = safe_request(page_url)

        if page_data and 'items' in page_data:
            all_flats_raw.extend(page_data['items'])
        else:
            print(f"Ошибка получения страницы {page} для проекта {slug}, пропускаем.")

# 4. Теперь «разворачиваем» каждую квартиру с помощью flatten_json
all_flats_flat = []
for flat in all_flats_raw:
    # flatten_json возвращает список «строк» (словарей),
    # поэтому расширяем общий список
    flat_rows = flatten_json(flat, parent_key="")
    all_flats_flat.extend(flat_rows)

# 5. Превращаем в DataFrame и сохраняем
df_flats = pd.DataFrame(all_flats_flat)
df_flats.to_csv("flats_expanded.csv", index=False, encoding="utf-8-sig")

print("Файл flats_expanded.csv успешно сохранён!")
