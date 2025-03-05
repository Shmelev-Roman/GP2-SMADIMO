import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm.auto import tqdm
import argparse

def parse_m2_card(html_code):
    """Парсим HTML одной карточки объявления с m2.ru
       и возвращаем словарь всех основных параметров.
    """
    soup = BeautifulSoup(html_code, "html.parser")
    
    info_dict = {}
    
    price_span = soup.find("span", {"itemprop": "price", "data-test": "offer-price"})
    if price_span:
        price = price_span.get("content")
        if not price:
            price = price_span.get_text(strip=True)
        info_dict["price"] = price
    
    
    info_items = soup.select('[data-test="infoItem"]')  
    for item in info_items:
        title_div = item.select_one('[data-test="infoItemTitle"]')
        value_div = item.select_one('[data-test="infoItemValue"]')
        
        if not title_div or not value_div:
            continue
        
        title_text = title_div.get_text(strip=True)
        value_text = value_div.get_text(strip=True)
        
        info_dict[title_text] = value_text
    
    return info_dict

def test_parse_m2(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/88.0.4324.96 Safari/537.36"
        )
    }
    
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        card_info = parse_m2_card(resp.text)
        return card_info
    else:
        print("Ошибка загрузки:", resp.status_code)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="None")
    parser.add_argument("--sector", type=str, required=True, help="Название сектора")

    args = parser.parse_args()

    df = pd.read_csv('links.csv')

    df = df[df.sector == args.sector]
    current_data = []

    for i, row in tqdm(df.iterrows()):
        res_d = test_parse_m2(row['link'])
        if res_d is not None:
            current_data.append(res_d)

    df_parsed = pd.DataFrame(current_data)
    df_parsed.to_csv(f"{args.sector}.csv", index=False)