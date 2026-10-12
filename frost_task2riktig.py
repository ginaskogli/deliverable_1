import requests
import pandas as pd
import matplotlib.pyplot as plt
import json

# GET TEMPERATURE DATA

with open('met_id.txt') as f:
    client_id = f'{f.readline().strip().split(':')[1]}'


def get_temperature_data():

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

    # Issue an HTTP GET request, r is in JSON format
    r = requests.get(endpoint, parameters, auth=(client_id,''))
    # Extract JSON data, make this a Python dictionary
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

    # Lager en ny dataframe for dato og temperatur
    temperature_df = df[['referenceTime', 'value']].copy()

    temperature_df = temperature_df.rename(
        columns={
            'referenceTime': 'date',
            'value': 'temperature',
        }
    )

    temperature_df['date'] = pd.to_datetime(temperature_df['date'])

    temperature_df['temperature'] = pd.to_numeric(temperature_df['temperature'])

    return temperature_df









# GET PRECIPITATION DATA
def get_precipitation_data():
    # Define endpoint and parameters
    endpoint = 'https://frost.met.no/observations/v0.jsonld'
    parameters = {
        'sources': 'SN17850',
        'elements': 'sum(precipitation_amount P1D)',
        'referencetime': '2025-01-01/2026-01-01',
        'timeoffsets': 'default',
        'levels': 'default',
        }
    # må sette sluttdato til 26-01-01 fordi de bruker åpne intervaller og dermed ikke inkluderer siste dato

    # Issue an HTTP GET request, r is in JSON format
    r = requests.get(endpoint, parameters, auth=(client_id,''))
    # Extract JSON data, make this a Python dictionary
    data = r.json()
    #print(json.dumps(data, indent=4))


    # Check if the request worked, print out any errors
    if r.status_code == 200:
        data = data['data']
        print('Data retrieved from frost.met.no!')
    else:
        print('Error! Returned status code %s' % r.status_code)
        print('Message: %s' % data['error']['message'])
        print('Reason: %s' % data['error']['reason'])


    # not all elements in data has observations, need to check for that before creating the dataframe
    for item in data:
        if 'observations' in item:
            df = pd.json_normalize(data, record_path='observations', meta=['referenceTime', 'sourceId'],)

    # make dafaframe for date and precipitation
    precipitation_df = df[['referenceTime', 'value']].copy()

    precipitation_df = precipitation_df.rename(
        columns={
            'referenceTime': 'date',
            'value': 'precipitation',
        }
    )
    precipitation_df['date'] = pd.to_datetime(precipitation_df['date'])

    return precipitation_df







# MAKE PLOT WITH TEMPERATURE FROM TASK 1 + PRECIPITATION

fig1, ax1 = plt.subplots()

ax1.plot(temperature_df['date'], temperature_df['temperature'])


ax2 = ax1.twinx()

ax2.plot(temperature_df['date'], precipitation_df['precipitation'])


plt.show()
