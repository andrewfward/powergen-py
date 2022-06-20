# -*- coding: utf-8 -*-
"""

    PV Ouput Subsystem for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
    Based on Python example in renewables.ninja API documentation
    https://www.renewables.ninja/documentation/api/python-example

"""

import requests
import pandas as pd
import json

def automatic_tilt(lati):
    """
    Original author: Stefan Pfenninger
    As found at: https://github.com/renewables-ninja/gsee/blob/master/gsee/pv.py
    
    Return optimal tilt angle for given latitude.
    Works for latitudes between 0 and 50 deg.
    Assumes panel is facing equator (azim = 180 deg)

    Parameters
    ----------
    lati : flaot
        Latitude in degrees.

    Returns
    -------
    angle : fkiat
        Optimal tilt angle in degrees.

    """
    lati = abs(lati)
    if lati <= 25:
        return lati * 0.87
    elif lati <= 50:
        return lati * 0.76 + 3.1
    else:
        return 40

def pv_output(lati, long, year, capacity, dataset="merra2", system_loss=0, auto_tilt=True, tilt=0, azim=180):

    if auto_tilt == True:
        azim = 180
        tilt = automatic_tilt(lati)
        
    start_date = str(year) + "-01-01"
    end_date = str(year) + "-12-31"    

    token = ' fc5b9e4dc8ef24a5923256436575c37dc8ce9195'
    # url for PV data
    url = 'https://www.renewables.ninja/api/data/pv'
    
    s = requests.session()
    # Send token header with each request
    s.headers = {'Authorization': 'Token ' + token}
    
    args = {
        'lat': lati,
        'lon': long,
        'date_from': start_date,
        'date_to': end_date,
        'dataset': dataset,
        'capacity': capacity,
        'system_loss': system_loss,
        'tracking': 0,      # assuming fixed, tracking panels are more expensive and harder to maintain.
        'tilt': tilt,
        'azim': azim,
        'header': False,
        'local_time': True,
        'format': 'json'
    }
    
    r = s.get(url, params=args)
    
    # Parse JSON to get a pandas.DataFrame of data and dict of metadata
    parsed_response = json.loads(r.text)
    
    data = pd.read_json(json.dumps(parsed_response), orient='index')
    
    return data["electricity"].values.tolist()
    # return data