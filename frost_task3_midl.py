
# lager en fil utenom for jeg tør ikke å begyne på en ny branch når jeg enda ikke er sikker 
# på om branchen oppgave2 er der den skal være, og at jeg ikke er i main?

# copy the whole function from task 2 instead of changing it to have a variable for referencetime,
# to avoid having to cange every other code that uses that function


import requests
import pandas as pd
import matplotlib.pyplot as plt
import json



def get_frost_data(desired_element, timeseries):

#"""

#        timeseries: formate '{start}/{end}' as 'yyyy-mm-dd/yyyy-mm-dd'

#"""    
    with open('met_id.txt') as f:
        client_id = f'{f.readline().strip().split(':')[1]}'

    # Define endpoint and parameters
    endpoint = 'https://frost.met.no/observations/v0.jsonld'
    parameters = {
        'sources': 'SN17850',
        'elements': f'{desired_element}',
        'referencetime': f'{timeseries}',
        'timeoffsets': 'default',
        'levels': 'default',
        }
    # set end date to 26-01-01 because they use open intervals, dont include last date

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
    # creates dataframe with observations (value, moh, unit MM.), referenceTime and sourceId
    for item in data:
        if 'observations' in item:
            dataframe = pd.json_normalize(data, record_path='observations', meta=['referenceTime', 'sourceId'],)

    return dataframe 

print(get_frost_data('mean(air_temperature P1D)', '2025-01-01/2026-01-01'))


# function for making dataframes containing only date and temperature

def temps_for_interval(df):
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


temps_2025 = temps_for_interval(get_frost_data('mean(air_temperature P1D)', '2025-01-01/2026-01-01'))
temps_1925 = temps_for_interval(get_frost_data('mean(air_temperature P1D)', '1925-01-01/1926-01-01'))


# make plot for 
x = range(365)
fig1, ax1 = plt.subplots()

ax1.plot(x, temps_2025['temperature'], color='tab:blue')
ax1.set_xlabel('Day of year')
ax1.set_ylabel('2025 temperatures C', color ='blue')

ax2 = ax1.twinx()

ax2.plot(x, temps_1925['temperature'], color='tab:orange')
ax2.set_xlabel('Date')
ax2.set_ylabel('1925 temperatures C', color = 'orange')

plt.show()