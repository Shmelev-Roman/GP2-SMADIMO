import requests
import json
import pandas as pd

session = requests.Session()

mortage = json.loads(
    session.get(     
        url='https://fsk.ru/api/mortgage/'
    ).content
)

with open('mortage.json', 'w', encoding='utf-8') as f:
    json.dump(mortage, f, ensure_ascii=False, indent=4)


# Convert JSON to DataFrame
df = pd.json_normalize(mortage)

# Save to CSV
csv_filename = "mortage.csv"
df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
