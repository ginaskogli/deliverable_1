# 1 henter maksimaltemperatur for valgt stasjon og år fra Frost - get_mac_temperature
# 2 teller hetebølger basert på temperaturdataene - count_heatwaves()
# 3 skriver resultatet til en YAML-fil - write_heatwave_summary()

import pandas as pd
import requests
import yaml 


def get_max_temperature(
    station_id: str,
    year: int,
) -> pd.DataFrame:
    """Retrive daily maximum temperatures for a station and year.

    Arguments:
        station_id: Frost station ID.
        year: Yer for which to retrive temperatures.

    Returns:
        DataFrame containing dates and daily maximum temperatures.
    """

    with open('met_id.txt', encoding="utf-8") as file:
        client_id = file.readline().strip().split(':')[1]

    # Define endpoint and parameters
    endpoint = 'https://frost.met.no/observations/v0.jsonld'
    parameters = {
        'sources': station_id,
        'elements': 'max(air_temperature P1D)',
        'referencetime': f"{year}-01-01/{year + 1}-01-01",
        'timeoffsets': 'default',
        'levels': 'default',
        }

    # Issue an HTTP GET request
    response = requests.get(
        endpoint,
        parameters, 
        auth=(client_id,''),
        timeout=30,
        )
    # timeout=30 - det er en begrensning av forespørselstid til systemet, går det mer enn 30 sek slutter den forespørselen

    # Extract JSON data
    response_data = response.json()

    # Check if the request worked, print out any errors
    if response.status_code == 200:
        # Convert the observations to DataFrame
        observations = pd.json_normalize(
            response_data['data'],
            record_path="observations",
            meta=['referenceTime', 'sourceId'],
        )

        temperature_df = observations[
            ['referenceTime', 'value']
        ].copy()

        temperature_df = temperature_df.rename(
            columns={
                "referenceTime": "date",
                "value": "temperature",
            }
        )

        print(temperature_df.columns)

        # konverterer dato til datetime for at det skal kunne leses
        temperature_df['date'] = pd.to_datetime(
            temperature_df['date']
        )
        # konverterer temperatur til numerisk verdi så det skal kunne leses
        temperature_df['temperature'] = pd.to_numeric(
            temperature_df['temperature']
        )

        return temperature_df

    else:
        raise RuntimeError(
            f"Frost request failed with status code"
            f"{response.status_code}: {response.text}"
        )

# Kaller funksjonen
temperature_df = get_max_temperature(
    station_id="SN17850",
    year=2025,
)

print(temperature_df.head())
print(temperature_df.shape)
