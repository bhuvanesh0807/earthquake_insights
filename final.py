import requests
import pandas as pd
import time
from datetime import datetime

all_records = []

current_date = datetime.now()
start_year = current_date.year - 5
end_year = current_date.year

print(f"🚀 Starting Data Extraction for {start_year} - {end_year}...")

for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        
        start_date = f"{year}-{month:02d}-01"
        
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
            
        if datetime.strptime(start_date, "%Y-%m-%d") > current_date:
            break
            
        params = {
            "format": "geojson",
            "starttime": start_date,
            "endtime": end_date,
            "minmagnitude": 2.5 }
        
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                features = data.get('features', [])
                
                for feature in features:
                    props = feature['properties']
                    geom = feature['geometry']
                    
                    record = {
    
                        'id': feature['id'],
                        'type': props.get('type'),
                        
                        'time': props.get('time'),
                        'updated': props.get('updated'),
                        
                        'latitude': geom['coordinates'][1],
                        'longitude': geom['coordinates'][0],
                        'depth_km': geom['coordinates'][2],
                        'place': props.get('place'),
                        
                        'mag': props.get('mag'),
                        'magType': props.get('magType'),
                        
                        'status': props.get('status'),
                        'tsunami': props.get('tsunami'),
                        'sig': props.get('sig'),
                        'net': props.get('net'),
                        
                        'nst': props.get('nst'),
                        'dmin': props.get('dmin'),
                        'rms': props.get('rms'),
                        'gap': props.get('gap'),
                        'magError': props.get('magError'),
                        'depthError': props.get('depthError'),
                        'magNst': props.get('magNst'),
                        'locationSource': props.get('locationSource'),
                        'magSource': props.get('magSource'),
                        'types': props.get('types'),
                        'ids': props.get('ids'),
                        'sources': props.get('sources')
                    }
                    all_records.append(record)
                print(f"✅ {start_date}: Found {len(features)} quakes")
            else:
                print(f"❌ {start_date}: Failed {response.status_code}")
                
        except Exception as e:
            print(f"⚠️ Error on {start_date}: {e}")
            
        # Sleep to be polite to the API server
        time.sleep(0.5)

print(f"\n🎉 Extraction Complete! Total Records: {len(all_records)}")

import pandas as pd
import re
from sqlalchemy import create_engine, text

df = pd.DataFrame(all_records)

df['time'] = pd.to_datetime(df['time'], unit='ms')
df['updated'] = pd.to_datetime(df['updated'], unit='ms')

def extract_country_regex(place_str):
    if pd.isna(place_str): return "Unknown"
    match = re.search(r',\s*([^,]+)$', place_str)
    if match:
        return match.group(1).strip()
    return place_str 

df['country'] = df['place'].apply(extract_country_regex)

df['year'] = df['time'].dt.year
df['month'] = df['time'].dt.month
df['day_of_week'] = df['time'].dt.day_name()

numeric_cols = ['mag', 'depth_km', 'nst', 'gap', 'dmin', 'rms', 'magError', 'depthError']
for col in numeric_cols:
    df[col] = df[col].fillna(0)

print(f"Data Cleaned. Shape: {df.shape}")
print(df[['time', 'place', 'country', 'mag']].head())

DB_USER = 'root'
DB_PASS = 'Bhuvanesh7871'  # <--- REPLACE THIS
DB_HOST = 'localhost'
DB_NAME = 'earthquake_db'

connection_str = f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}"
engine = create_engine(connection_str)

with engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}"))
    conn.execute(text(f"USE {DB_NAME}"))
conn.commit()

db_engine = create_engine(f"{connection_str}/{DB_NAME}")

try:
    print("⏳ Uploading to MySQL...")
    df.to_sql('earthquakes', con=db_engine, if_exists='replace', index=False, chunksize=1000)
    print("✅ Success! Data stored in MySQL table 'earthquakes'.")
except Exception as e:
    print(f"❌ Database Error: {e}")




             
