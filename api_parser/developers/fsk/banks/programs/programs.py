import requests
import json
import pandas as pd

session = requests.Session()

programs = json.loads(
    session.get(     
        url='https://fsk.ru/api/v3/mortgage/program/types'
    ).content
)

# Convert JSON to DataFrame
df = pd.json_normalize(programs)

# Save to CSV
csv_filename = "programs.csv"
df.to_csv(csv_filename, index=False, encoding="utf-8-sig")
