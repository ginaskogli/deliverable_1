

import requests
import pandas as pd
#import matplotlib.pyplot as plt

with open('met_id.txt') as f:
    client_id = f'{f.readline().strip().split(':')[1]}'

# Define endpoint and parameters
endpoint = 'https://frost.met.no/observations/v0.jsonld'
parameters = {
    'sources': 'SN17850',
    'elements': 'mean(air_temperature P1D)',
    'referencetime': '2025-01-01/2026-01-01',
    'timeoffsets': 'default',
    'levels': 'default',
    }
# må sette sluttdato til 26-01-01 fordi de bruker åpne intervaller og dermed ikke inkluderer siste dato

# Issue an HTTP GET request
r = requests.get(endpoint, parameters, auth=(client_id,''))
# Extract JSON data
data = r.json()

# Check if the request worked, print out any errors
if r.status_code == 200:
    data = data['data']
    print('Data retrieved from frost.met.no!')
else:
    print('Error! Returned status code %s' % r.status_code)
    print('Message: %s' % data['error']['message'])
    print('Reason: %s' % data['error']['reason'])

# This will return a Dataframe with all of the observations in a table format
# Convert the observations to a DataFrame
df = pd.json_normalize(
    data,
    record_path='observations',
    meta=['referenceTime', 'sourceId'],
)

df.head()

print(df.head())

# Lager en ny dataframe for dato og temperatur
temperature_df = df[['referenceTime', 'value']].copy()

temperature_df = temperature_df.rename(
    columns={
        'referenceTime': 'date',
        'value': 'temperature',
    }
)

temperature_df['date'] = pd.to_datetime(
    temperature_df['date']
)

temperature_df['temperature'] = pd.to_numeric(
    temperature_df['temperature']
)

print(temperature_df.head())

# Sjekker hvilke data vi har
print(temperature_df.shape)

print(temperature_df['date'].min())
print(temperature_df['date'].max())

def temperature_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate summary statistics for the temperature data.

    Arguments:
    df: DataFrame containing a 'temperature' column.

    Returns:
    DataFrame containing the mean, median, minimum and maximum temperature."""
    summary = pd.DataFrame({
        'temperature': [
            df['temperature'].mean(),
            df['temperature'].median(),
            df['temperature'].min(),
            df['temperature'].max(),
        ]
    }, index=['mean', 'median', 'min', 'max'])

    return summary

summary = temperature_summary(temperature_df)

print(summary)