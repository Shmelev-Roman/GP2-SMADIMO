import requests
import json
import pandas as pd

session = requests.Session()

banks = json.loads(
    session.get(     
        url='https://fsk.ru/api/banks/'
    ).content
)

# Convert JSON to DataFrame
df = pd.json_normalize(banks)

# Save to CSV
csv_filename = "banks.csv"
df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
