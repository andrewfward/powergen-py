# -*- coding: utf-8 -*-
"""

    PV Ouput Subsystem for "Energy 4 Development" VIP
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    Based on MATLAB code by Steven Nolan ( )

"""

import requests
import pandas as pd
import json

token = 'fc5b9e4dc8ef24a5923256436575c37dc8ce9195'
api_base = 'https://www.renewables.ninja/api/'

s = requests.session()
# Send token header with each request
s.headers = {'Authorization': 'Token ' + token}


##
# PV example
##

url = api_base + 'data/pv'

args = {
    'lat': 34.125,
    'lon': 39.814,
    'date_from': '2015-01-01',
    'date_to': '2015-12-31',
    'dataset': 'merra2',
    'capacity': 1.0,
    'system_loss': 0.1,
    'tracking': 0,
    'tilt': 35,
    'azim': 180,
    'format': 'json'
}

r = s.get(url, params=args)

# Parse JSON to get a pandas.DataFrame of data and dict of metadata
parsed_response = json.loads(r.text)

data = pd.read_json(json.dumps(parsed_response['data']), orient='index')
metadata = parsed_response['metadata']