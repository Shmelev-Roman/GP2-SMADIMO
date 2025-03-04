import requests
import json
import pandas as pd

session = requests.Session()

cities = json.loads(
    session.get(     
        url='https://fsk.ru/api/city/'
    ).content
)

with open('cities.json', 'w', encoding='utf-8') as f:
    json.dump(cities, f, ensure_ascii=False, indent=4)


# Convert JSON to DataFrame
df = pd.json_normalize(cities)

# Save to CSV
csv_filename = "cities.csv"
df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
