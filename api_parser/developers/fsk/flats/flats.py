import logging
import pandas as pd

from api_parser.utils import parsing
from api_parser.data import config

# Инициализация логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """
    Основная логика:
    1. Получаем список проектов
    2. Формируем список slug для проектов
    3. Сбор всех квартир
    4. "Разворачиваем" каждую квартиру с помощью parsing.flatten_json
    5. Превращаем результат в DataFrame и сохраняем в CSV
    """

    # 1. Получаем список проектов
    projects_url = config.FSK_API_URL + 'v3/projects/all'
    projects_data = parsing.safe_request(projects_url, logger=logger)

    if not projects_data:
        logger.error("Не удалось получить список проектов. Завершаем работу.")
        return

    # 2. Получаем slugs всех проектов
    projects_slugs = [p.get('slug') for p in projects_data if p.get('slug')]
    logger.info(f"Найдено проектов: {len(projects_slugs)}")

    # 3. Сбор всех квартир в единый список
    all_flats_raw = []

    for slug in projects_slugs:
        logger.info(f"Обрабатываем проект: {slug}")
        first_page_url = f'{config.FSK_API_URL}v3/flats/?order=asc&page=1&project_slug={slug}'
        first_page_data = parsing.safe_request(first_page_url, logger=logger)

        if not first_page_data:
            logger.warning(f"Пропускаем проект {slug} из-за ошибки запроса.")
            continue

        total_pages = first_page_data.get('totalPages', 1)
        all_flats_raw.extend(first_page_data.get('items', []))

        for page in range(2, total_pages + 1):
            page_url = f'{config.FSK_API_URL}v3/flats/?order=asc&page={page}&project_slug={slug}'
            page_data = parsing.safe_request(page_url, logger=logger)

            if page_data and 'items' in page_data:
                all_flats_raw.extend(page_data['items'])
            else:
                logger.warning(f"Ошибка получения страницы {page} для проекта {slug}, пропускаем.")

    logger.info(f"Общее количество загруженных квартир: {len(all_flats_raw)}")

    # 4. «Разворачиваем» каждую квартиру с помощью parsing.flatten_json
    all_flats_flat = []
    for idx, flat in enumerate(all_flats_raw):
        # Добавляем оригинальный ID квартиры для идентификации
        flat['original_flat_id'] = idx

        # Разворачиваем
        flat_rows = parsing.flatten_json(flat)
        all_flats_flat.extend(flat_rows)

        # Выводим прогресс каждые 100 квартир
        if (idx + 1) % 100 == 0:
            logger.info(f"Обработано {idx + 1} квартир из {len(all_flats_raw)}")

    # 5. Превращаем в DataFrame и сохраняем
    df_flats = pd.DataFrame(all_flats_flat)
    df_flats.to_csv("flats_expanded.csv", index=False, encoding="utf-8-sig")

    logger.info(f"Файл flats_expanded.csv успешно сохранён! Всего строк: {len(df_flats)}")

    # Выводим информацию о результатах
    flat_ids = df_flats['original_flat_id'].nunique() if 'original_flat_id' in df_flats.columns else 0
    logger.info(f"Исходных квартир: {len(all_flats_raw)}")
    logger.info(f"Уникальных ID квартир в результате: {flat_ids}")
    logger.info(f"Среднее количество строк на квартиру: {len(df_flats) / max(1, len(all_flats_raw)):.2f}")


if __name__ == "__main__":
    main()
