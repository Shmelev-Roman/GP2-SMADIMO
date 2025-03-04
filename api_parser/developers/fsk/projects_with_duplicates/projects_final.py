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

def flatten_json(nested_data, parent_key="", max_depth=5):
    """
    Разворачиваем JSON до заданной глубины.
    """
    results = []
    
    # Если глубина закончилась – вернуть как есть (словарь или список, но уже не лезть глубже)
    if max_depth <= 0:
        # Вернем "сырой" контент как одну строку в виде JSON-строки (или как есть)
        return [{parent_key: nested_data}] if parent_key else [{"_data": nested_data}]

    if isinstance(nested_data, dict):
        base_row = {}
        list_fields = {}
        dict_fields = {}

        for key, value in nested_data.items():
            new_key = f"{parent_key}_{key}" if parent_key else key
            
            if isinstance(value, dict):
                dict_fields[new_key] = value
            elif isinstance(value, list):
                list_fields[new_key] = value
            else:
                base_row[new_key] = value

        # Если только примитивы – вернуть сразу
        if not list_fields and not dict_fields:
            return [base_row]
        
        dict_results = []
        for k, v in dict_fields.items():
            nested_rows = flatten_json(v, k, max_depth - 1)
            if not dict_results:
                for nr in nested_rows:
                    dict_results.append({**base_row, **nr})
            else:
                new_results = []
                for existing_row in dict_results:
                    for nr in nested_rows:
                        new_results.append({**existing_row, **nr})
                dict_results = new_results

        if not dict_results and base_row:
            dict_results = [base_row]

        list_results = []
        for k, values in list_fields.items():
            if all(isinstance(it, dict) for it in values):
                for item in values:
                    nested_rows = flatten_json(item, k, max_depth - 1)
                    if not dict_results and not list_results:
                        for nr in nested_rows:
                            list_results.append({**base_row, **nr})
                    elif dict_results and not list_results:
                        for row in dict_results:
                            for nr in nested_rows:
                                list_results.append({**row, **nr})
                    elif not dict_results and list_results:
                        new_results = []
                        for row in list_results:
                            for nr in nested_rows:
                                new_results.append({**row, **nr})
                        list_results = new_results
                    else:
                        new_results = []
                        for row in dict_results:
                            for nr in nested_rows:
                                new_results.append({**row, **nr})
                        list_results.extend(new_results)
            else:
                # Список примитивов
                str_value = ", ".join(str(x) for x in values)
                if not dict_results and not list_results:
                    base_row[k] = str_value
                    list_results.append(base_row)
                elif dict_results and not list_results:
                    for row in dict_results:
                        row[k] = str_value
                    list_results = dict_results
                elif list_results:
                    for row in list_results:
                        row[k] = str_value
        
        if list_results:
            results.extend(list_results)
        elif dict_results:
            results.extend(dict_results)
        else:
            results.append(base_row)

    elif isinstance(nested_data, list):
        for item in nested_data:
            results.extend(flatten_json(item, parent_key, max_depth - 1))
    else:
        # Примитив
        key = parent_key if parent_key else '_value'
        results.append({key: nested_data})

    return results


# -------------------------------------------------------
# Основная логика для сбора и сохранения данных по проектам
# -------------------------------------------------------
projects_url = 'https://fsk.ru/api/v3/projects/all'
projects_data = safe_request(projects_url)

if not projects_data:
    print("Не удалось получить список проектов. Завершаем работу.")
    exit()

# Достаем slugs
project_slugs = [p.get('slug') for p in projects_data if p.get('slug')]

all_projects_raw = []
for idx, slug in enumerate(project_slugs):
    print(f"Получаем данные по проекту: {slug}")
    project_url = f'https://fsk.ru/api/v3/projects/{slug}'
    project_info = safe_request(project_url)
    if project_info:
        project_info['project_slug'] = slug
        project_info['original_project_id'] = idx
        all_projects_raw.append(project_info)
    else:
        print(f"Ошибка или пустой ответ по проекту {slug}")

# «Разворачиваем» все проекты в плоскую структуру
all_projects_flat = []
for proj in all_projects_raw:
    flat_rows = flatten_json(proj)
    all_projects_flat.extend(flat_rows)

df_projects = pd.DataFrame(all_projects_flat)

# Сохраняем в CSV
df_projects.to_csv("projects_expanded.csv", index=False, encoding="utf-8-sig")
print(f"Файл projects_expanded.csv успешно сохранён! Всего строк: {len(df_projects)}")

print("Скрипт завершён.")
