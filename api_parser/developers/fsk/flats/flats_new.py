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
    Возвращает список словарей, где для каждого вложенного объекта 
    или элемента списка создается отдельная запись.
    """
    results = []
    
    # Базовый случай - словарь
    if isinstance(nested_data, dict):
        # Создаем базовую строку с примитивными значениями
        base_row = {}
        list_fields = {}  # словарь для хранения полей-списков
        dict_fields = {}  # словарь для хранения полей-словарей
        
        # Сначала извлекаем примитивные значения и запоминаем сложные
        for key, value in nested_data.items():
            new_key = f"{parent_key}_{key}" if parent_key else key
            
            if isinstance(value, dict):
                dict_fields[new_key] = value
            elif isinstance(value, list):
                list_fields[new_key] = value
            else:
                # Примитивное значение
                base_row[new_key] = value
        
        # Если в словаре только примитивные значения, возвращаем его
        if not list_fields and not dict_fields:
            return [base_row]
        
        # Обрабатываем вложенные словари
        dict_results = []
        for key, value in dict_fields.items():
            nested_rows = flatten_json(value, key)
            if not dict_results:
                # Первый вложенный словарь - просто добавляем все строки
                for nested_row in nested_rows:
                    combined_row = {**base_row, **nested_row}
                    dict_results.append(combined_row)
            else:
                # Последующие словари - для каждой существующей строки создаем несколько новых
                new_results = []
                for existing_row in dict_results:
                    for nested_row in nested_rows:
                        combined_row = {**existing_row, **nested_row}
                        new_results.append(combined_row)
                dict_results = new_results
        
        # Если нет вложенных словарей, но есть базовая строка, используем ее
        if not dict_results and base_row:
            dict_results = [base_row]
        
        # Обрабатываем поля-списки
        list_results = []
        for key, values in list_fields.items():
            # Для списка словарей
            if all(isinstance(item, dict) for item in values):
                # Разворачиваем каждый элемент списка
                for item in values:
                    nested_rows = flatten_json(item, key)
                    
                    # Если еще нет результатов (ни от dict_fields, ни от предыдущих list_fields)
                    if not dict_results and not list_results:
                        # Первый список - добавляем напрямую с базовой строкой
                        for nested_row in nested_rows:
                            combined_row = {**base_row, **nested_row}
                            list_results.append(combined_row)
                    elif dict_results and not list_results:
                        # Есть результаты от dict_fields, но не от list_fields
                        for existing_row in dict_results:
                            for nested_row in nested_rows:
                                combined_row = {**existing_row, **nested_row}
                                list_results.append(combined_row)
                    elif not dict_results and list_results:
                        # Есть результаты от предыдущих list_fields
                        new_results = []
                        for existing_row in list_results:
                            for nested_row in nested_rows:
                                combined_row = {**existing_row, **nested_row}
                                new_results.append(combined_row)
                        list_results = new_results
                    else:
                        # Есть результаты и от dict_fields, и от list_fields
                        # Используем dict_results как основу
                        new_results = []
                        for existing_row in dict_results:
                            for nested_row in nested_rows:
                                combined_row = {**existing_row, **nested_row}
                                new_results.append(combined_row)
                        list_results.extend(new_results)
            else:
                # Для списка примитивных значений
                # Преобразуем в строку, разделенную запятыми
                str_value = ", ".join(str(item) for item in values)
                
                if not dict_results and not list_results:
                    # Если еще нет результатов
                    base_row[key] = str_value
                    list_results.append(base_row)
                elif dict_results and not list_results:
                    # Если есть результаты от dict_fields
                    for row in dict_results:
                        row[key] = str_value
                    list_results = dict_results
                elif list_results:
                    # Если уже есть результаты от list_fields
                    for row in list_results:
                        row[key] = str_value
        
        # Собираем финальные результаты
        if list_results:
            results.extend(list_results)
        elif dict_results:
            results.extend(dict_results)
        else:
            results.append(base_row)
            
    # Случай, когда пришел список верхнего уровня
    elif isinstance(nested_data, list):
        for item in nested_data:
            item_rows = flatten_json(item, parent_key)
            results.extend(item_rows)
    else:
        # Если пришло примитивное значение (строка, число и т.д.)
        key = parent_key if parent_key else '_value'
        results.append({key: nested_data})
    
    return results


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

# 3. Сбор всех квартир в единый список
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

# 4. Теперь «разворачиваем» каждую квартиру с помощью новой функции flatten_json
all_flats_flat = []
for idx, flat in enumerate(all_flats_raw):
    # Добавляем оригинальный ID квартиры для идентификации
    flat['original_flat_id'] = idx
    
    # Разворачиваем каждую квартиру в несколько строк
    flat_rows = flatten_json(flat)
    all_flats_flat.extend(flat_rows)
    
    # Выводим прогресс
    if (idx + 1) % 100 == 0:
        print(f"Обработано {idx + 1} квартир из {len(all_flats_raw)}")

# 5. Превращаем в DataFrame и сохраняем
df_flats = pd.DataFrame(all_flats_flat)

# Сохраняем в CSV
df_flats.to_csv("flats_expanded.csv", index=False, encoding="utf-8-sig")
print(f"Файл flats_expanded.csv успешно сохранён! Всего строк: {len(df_flats)}")

# Выводим информацию о результатах
flat_ids = df_flats['original_flat_id'].nunique() if 'original_flat_id' in df_flats.columns else 0
print(f"Исходных квартир: {len(all_flats_raw)}")
print(f"Уникальных ID квартир в результате: {flat_ids}")
print(f"Среднее количество строк на квартиру: {len(df_flats) / max(1, len(all_flats_raw)):.2f}")