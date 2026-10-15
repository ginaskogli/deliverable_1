
import requests
import pandas as pd
import matplotlib.pyplot as plt


def get_frost_data(desired_element: str) -> pd.DataFrame:

    """Creates dataframe containing observations (value, moh, unit MM.), referenceTime and sourceId, 
    from website frost.no, at site SN17850 (Ås).

    Arguments:
        desired_element: weather element from element list at frost.no

    Returns:
        dataframe: observations for each day in timeseries.

    """ 

    with open('met_id.txt') as f:
        client_id = f.readline().strip().split(':')[1]

    # Define endpoint and parameters
        endpoint = 'https://frost.met.no/observations/v0.jsonld'
        parameters = {
            'sources': 'SN17850',
            'elements': desired_element,
            'referencetime': '2025-01-01/2026-01-01',
            'timeoffsets': 'default',
            'levels': 'default',
            }
        # set end date to 26-01-01 because they use open intervals, dont include last date
    
        # Issue an HTTP GET request, r is in JSON format
        r = requests.get(endpoint, parameters, auth=(client_id, ''))
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


def get_temperature_data(df: pd.DataFrame) -> pd.DataFrame:

    """Creates dataframes containing only date and temperature, from a dataframe of meteorological data.

    Arguments:
        df: a dataframe with columns 'observations', 'referenceTime' and 'sourceId' 

    Returns:
        df: a dataframe containing date and temperature

    """

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


def get_precipitation_data(df: pd.DataFrame) -> pd.DataFrame:

    """Creates dataframes containing only date and precipitation, from a dataframe of meteorological data.

    Arguments:
        df: a dataframe with columns 'observations', 'referenceTime' and 'sourceId'. 

    Returns:
        df: a dataframe containing date and precipitation.

    """
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


# gather dataframes for temperature and precepitation in simpler names
temp = get_temperature_data(get_frost_data('mean(air_temperature P1D)'))
prec = get_precipitation_data(get_frost_data('sum(precipitation_amount P1D)'))

# MAKE PLOT WITH TEMPERATURE FROM TASK 1 + PRECIPITATION
# create figure and first axis
fig1, ax1 = plt.subplots()

ax1.plot(temp['date'], temp['temperature'], color='tab:blue')
ax1.set_xlabel('Date')
ax1.set_ylabel('Temperature C', color = 'blue')

ax2 = ax1.twinx()

ax2.plot(temp['date'], prec['precipitation'], color='tab:orange')
ax2.set_xlabel('Date')
ax2.set_ylabel('Precipitation mm', color = 'orange')
plt.title('Temperature and precipitation 2025')
plt.show()
