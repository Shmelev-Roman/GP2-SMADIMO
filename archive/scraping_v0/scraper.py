# scraper.py
import pandas as pd
import logging
from page_parser import process_page

def scrape_pages():
    all_data = []
    max_pages = 1
    for p in range(1, max_pages+1):
        logging.info(f"Начало обработки страницы {p}")
        page_data = process_page(p)
        all_data.extend(page_data)
    
    df = pd.DataFrame(all_data)
    df.drop_duplicates(subset=["offerId"], inplace=True)
    out_csv = "flats.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")
    logging.info(f"Сохранено {len(df)} уникальных записей в {out_csv}")
