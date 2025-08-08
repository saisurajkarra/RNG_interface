import json
import os

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def update_cached_lead(company, enrichment, path='data/enriched_epcs.csv'):
    import pandas as pd
    try:
        df = pd.read_csv(path)
    except:
        df = pd.DataFrame(columns=['Company', 'Enrichment'])
    new_row = pd.DataFrame([[company, enrichment]], columns=['Company', 'Enrichment'])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(path, index=False)