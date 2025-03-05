import time
import requests


def safe_request(url, logger, retries=3, timeout=10):
    """Безопасный GET-запрос с повторными попытками."""
    for attempt in range(retries):
        try:
            logger.info(f"Отправляем запрос к {url} (попытка {attempt + 1}/{retries})")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса {url}: {e} (попытка {attempt + 1}/{retries})")
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

                if not dict_results and not list_results:   # Если еще нет результатов
                    base_row[key] = str_value
                    list_results.append(base_row)
                elif dict_results and not list_results:     # Если есть результаты от dict_fields
                    for row in dict_results:
                        row[key] = str_value
                    list_results = dict_results
                elif list_results:                          # Если уже есть результаты от list_fields
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
