import pandas as pd
import requests
import yaml 


def get_max_temperature(
    station_id: str,
    year: int,
) -> pd.DataFrame:
    """Retrieve daily maximum temperatures for a station and year.

    Arguments:
        station_id: Frost station ID.
        year: Year for which to retrive temperatures.

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
        params=parameters, 
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


# Heatwave deffined as 5 consecutive days with T_max>=27*C
def find_heatwaves(df: pd.DataFrame) -> list[tuple[str, str]]:
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
    consecutive_days = 0    # Når det er registrert en varm dag øker den med en

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


def summarize_heatwaves(
    heatwaves: list[tuple[str, str]],
    station_id: str,
    station_name: str,
    year: int,
) -> dict:
    """Create a summary of heatwaves for a station and year.

    Arguments:
        heatwaves: List of start and end dates for each heatwave.
        station_id: ID fo the weather station.
        station_name: Name of the weather station.
        year: Year for which heatwaves are summarized.

    Returns:
        A dictionary containing the heatwave dates, station ID,
        station name, and year.
    """
    # Formatting the dates from tuples to strings, in new list
    formatted_dates = [f"{start_date} - {end_date}" for start_date, end_date in heatwaves]

    summary = {
        "dates": formatted_dates,
        "station_id": station_id,
        "station_name": station_name,
        "year": year,
    }

    return summary


def write_heatwaves_to_yaml(summary: dict, filename: str) -> None:
    """Write a heatwave summary to a YAML file.

    Arguments:
        summary: Dictionary containing the heatwave summary.
        filename: Name of the YAML file to write.

    Returns:
        None.
    """
    with open(filename, "w", encoding="utf-8") as file:
        # encoding=utf-8, sørger for at tekst inkludert Å blir håndtert riktig
        # as file - navn så vi kan skrive fil
        yaml.dump(summary, file, allow_unicode=True, sort_keys=False)
        # allow_unicode=True - tillater bokstaver som Å kan skrives i filen
        # sort_keys=False gjør at nøkler beholdes i samme rekkefølge som i dict


# Calling the function - here we put in the station id and year, so it works for different stations
temperature_df = get_max_temperature(
    station_id="SN17850",
    year=2025,
)

# Finding heatwaves form the datasett
heatwaves = find_heatwaves(temperature_df)

# Runn with formatted dates
summary = summarize_heatwaves(
    heatwaves=heatwaves,
    station_id="SN17850",
    station_name="Ås",
    year=2025,
)

# Kall funksjonen og lag filnavn
write_heatwaves_to_yaml(summary=summary, filename="heatwave_summary.yml")
