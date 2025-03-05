import pandas as pd
import logging

from api_parser.utils import parsing
from api_parser.data import config


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """
    Основная функция выполнения скрипта:
    1. Получение списка проектов
    2. Получение прогресса для каждого проекта
    3. Сохранение данных в CSV
    4. Вывод нескольких строк для проверки
    """

    # 1. Получаем список проектов
    projects_url = config.FSK_API_URL + 'v3/projects/all'
    projects_data = parsing.safe_request(projects_url, logger=logger)

    if not projects_data:
        logger.error("Не удалось получить список проектов. Завершаем работу.")
        return

    # 2. Получаем полную информацию о прогрессе для каждого проекта
    all_project_progress = []
    for project in projects_data:
        slug = project.get('slug')
        if not slug:
            logger.warning("В данных проекта отсутствует slug. Пропускаем.")
            continue

        progress_url = f'https://fsk.ru/api/complex/{slug}/progress/'
        progress_data = parsing.safe_request(progress_url, logger=logger)

        if progress_data and 'items' in progress_data:
            # Добавляем slug проекта к каждой записи о прогрессе
            for item in progress_data['items']:
                item['project_slug'] = slug

            all_project_progress.extend(progress_data['items'])
            logger.info(f"Получен прогресс для проекта: {slug}")
        else:
            logger.warning(f"Не удалось получить прогресс для проекта: {slug}")

    # 3. Сохраняем данные в CSV
    if all_project_progress:
        df_progress = pd.DataFrame(all_project_progress)

        # Сохраняем в CSV
        df_progress.to_csv("project_progress.csv", index=False, encoding="utf-8-sig")

        logger.info("Файл project_progress.csv успешно сохранён!")
        logger.info(f"Всего записей о прогрессе: {df_progress.__len__()}")
        logger.info(f"Количество уникальных проектов: {df_progress['project_slug'].nunique()}")
    else:
        logger.warning("Не удалось получить данные о прогрессе проектов.")

    # 4. Вывод первых нескольких строк для проверки
    if all_project_progress:
        df_progress = pd.DataFrame(all_project_progress)
        logger.info("Первые 5 записей для проверки:")
        logger.info("\n" + df_progress.head().to_string())


if __name__ == '__main__':
    main()