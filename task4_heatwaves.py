# 1 henter maksimaltemperatur for valgt stasjon og år fra Frost - get_max_temperature
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

# Calling the function - here we put in the station id and year, so it works for different stations
temperature_df = get_max_temperature(
    station_id="SN17850",
    year=2025,
)


# Heatwave deffined as 5 consecutive days with T_max>=27*C
def find_heatwaves(df: pd.DataFrame) -> list[str, str]:
    """Find heatwaves, defined as five or more consecutive days,
    with temperatures of 27 degrees or more.

    Arguments:
        df: DataFrame containing 'date' and 'temperature' columns.

    Returns:
        A list of tuples containing the start and end dates of each heatwave.
    """

    hot_days = df['temperature'] >= 27

    # Variables for the colected data
    heatwaves = []  # List that will collect start/end dates for heatwaves
    start_date = None   # We dont know when a heatwave wil start, so therefore None, will contain timestamps later,
        # None er en pythonverdi som betyr at vi ikke har en verdi her enda, enda ikke registrert en varm periode i starten
    consecutive_days = 0    #Når det er registrert en varm dag øker den med en

    for index, is_hot in enumerate(hot_days):
        # index - plassering til dagen i dataframe
        # is_hot - gir true/false statement om den dagen
        if is_hot:
            if consecutive_days == 0:
                start_date = df.iloc[index]['date']

            consecutive_days += 1

        # Nå undersøke om perioden var >=5 dager
        # hvis ja, lagre hetebølge
        # Så nullstille telleren så vi begynner på nytt
        else:
            if consecutive_days >= 5:
                end_date = df.iloc[index - 1]['date']   # iloc henter raden på aktuell plassering

                # strftime formaterer datoen
                heatwaves.append(
                    (
                        start_date.strftime("%Y-%m-%d"),
                        end_date.strftime("%Y-%m-%d"),
                    )
                )

            consecutive_days = 0
            start_date = None

    # håndtering av hetebølge på slutten av året som ikke avslutter med temperatur >27
    if consecutive_days >= 5:
        end_date = df.iloc[-1]['date']  # iloc[-1] henter siste rad i datasettet
        heatwaves.append(
            (
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
            )
        )

    return heatwaves


# Testing med laget lite datasett
# skal fungere - hetebølge
test_df_hw = pd.DataFrame({
    "date": pd.date_range("2025-07-01", periods=5),
    "temperature": [28, 29, 30, 28, 27]
})

print("test_hw:", find_heatwaves(test_df_hw))

# skal ikke fungere - periode for kort
test_df_short = pd.DataFrame({
    "date": pd.date_range("2025-07-01", periods=5),
    "temperature": [28, 29, 30, 28, 24],
})

print("test_short:", find_heatwaves(test_df_short))

# skal fungere - hetebølge fortsetter til siste dag av datasett
# Tester hetebølge som fortsetter til siste dag
test_df_new_year = pd.DataFrame({
    "date": pd.date_range("2025-12-27", periods=6),
    "temperature": [24, 28, 29, 30, 28, 27],
})

print("test_new_year:", find_heatwaves(test_df_new_year))

# Finding heatwaves form the datasett
heatwaves = find_heatwaves(temperature_df)

print("MET data:", heatwaves)

# kontroll av temperaturmålinger for registrerte hetebølger
for start_date, end_date in heatwaves:
    print(f"Heatwave: {start_date} to {end_date}")

    mask = (
        (temperature_df['date'] >= start_date)
        & (temperature_df['date'] <= end_date)
    )

    print(temperature_df.loc[mask])
