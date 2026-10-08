

import requests
import pandas as pd

with open('met_id.txt') as f:
    client_id = f'{f.readline().strip().split(':')[1]}'

# Define endpoint and parameters
endpoint = 'https://frost.met.no/observations/v0.jsonld'
parameters = {
    'sources': 'SN17850',
    'elements': 'mean(air_temperature P1D),
    'referencetime': '2025-01-01/2025-12-31',
    'timeoffsets': 'default',
    'levels': 'default',
    }

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
df = pd.DataFrame()
for i in range(len(data)):
    row = pd.DataFrame(data[i]['observations'])
    row['referenceTime'] = data[i]['referenceTime']
    row['sourceId'] = data[i]['sourceId']
    df = df.append(row)

df = df.reset_index()

df.head()

{
  "@context": "https://frost.met.no/schema",
  "@type": "LocationResponse",
  "apiVersion": "v0",
  "license": "https://creativecommons.org/licenses/by/3.0/no/",
  "createdAt": "2026-10-08T10:19:58Z",
  "queryTime": 0.002,
  "currentItemCount": 1,
  "itemsPerPage": 1,
  "offset": 0,
  "totalItemCount": 1,
  "currentLink": "https://frost.met.no/locations/v0.jsonld?names=%C3%85s",
  "data": [
    {
      "name": "Ås",
      "feature": "Small town",
      "geometry": {
        "@type": "Point",
        "coordinates": [
          10.794636,
          59.664717
        ],
        "nearest": False
      }
    }
  ]
}

