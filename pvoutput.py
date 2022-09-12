# -*- coding: utf-8 -*-
"""

    PV Ouput Subsystem for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
    Based on Python example in renewables.ninja API documentation.
    Original author: Stefan Pfenninger
    Available at: https://www.renewables.ninja/documentation/api/python-example

"""
"""
FUTURE WORK

- add error handling

"""

import requests
import json

import pandas as pd

def pv_output(lati, long, capacity, year=2019,
              auto_dataset=True, dataset="merra2", system_loss=0, 
              auto_tilt=True, tilt=40, azim=180):
    """
    Parameters
    ----------
    lati : flaot
        Location latitude (deg).
    long : float
        Location longitude (deg).
    year : int
        Data year.
    capacity : flaot
        Capacity of PV panel (Watts).
    dataset : string, optional
        Solar resources dataset.
        Options:
        NASA MERRA-2 ("merra2"):
            global coverage, 1980 - ongoing.
        CM-SAF SARAH ("sarah"):
            covers Europe, higher accuracy, 2000 - 2015. 
        The default is "merra2".
    system_loss : float, optional
        System's internal losses. Value between 0 and 1.
        The default is 0.
        (future work will account for this)
    auto_tilt : Boolean, optional
        If True, tilt is automatically calculated based on latitude.
        The default is True.
    tilt : flaot, optional
        PV panel tilt angle (deg). The default is 0.
    azim : float, optional
        PV panel azim angle (deg). The default is 180 (facing equator).

    Returns
    -------
    list
        Hourly power output for single PV panel with given capacity in
        selected year.

    """
    if auto_dataset == True:
        dataset = automatic_dataset(lati, long, year)
        print("dataset: " + dataset)
    
    if auto_tilt == True:
        azim = 180
        tilt = automatic_tilt(lati)
        print("tilt: " + str(tilt))
        
    start_date = str(year) + "-01-01"
    end_date = str(year) + "-12-31"    

    token = 'fc5b9e4dc8ef24a5923256436575c37dc8ce9195'     # Alfredo's account token.
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
        'capacity': capacity / 1000,    # from W to kW
        'system_loss': system_loss,
        'tracking': 0,                  # assuming fixed, tracking panels are more expensive and harder to maintain.
        'tilt': tilt,
        'azim': azim,
        'header': False,
        'local_time': True,
        'format': 'json'
    }
    
    print("Retrieving data from Renewables.ninja...")
    
    # Request JSON
    r = s.get(url, params=args)
    # Parse JSON to get a pandas.DataFrame of data
    parsed_response = json.loads(r.text)
    
    data = pd.read_json(json.dumps(parsed_response), orient='index')
    
    # return PV panel power output in Watts
    return [p_out * 1000 for p_out in data["electricity"].values.tolist()]

def automatic_tilt(lati):
    """
    Original author: Stefan Pfenninger
    As found at: https://github.com/renewables-ninja/gsee/blob/master/gsee/pv.py
    
    Stefan Pfenninger and Iain Staffell (2016).
    Long-term patterns of European PV output using 30 years of 
    validated hourly reanalysis and satellite data.
    Energy 114, pp. 1251-1265. doi: 10.1016/j.energy.2016.08.060
    
    Returns optimal tilt angle for given latitude.
    Works for latitudes between 0 and 50 deg, above 50 deg,
    tilt is set to 40 deg.
    Assumes panel is facing equator (azim = 180 deg)

    Parameters
    ----------
    lati : flaot
        Latitude in degrees.
    
    Returns
    -------
    float or int
        Optimal tilt angle for equator facing panel in degrees.

    """
    lati = abs(lati)
    
    if lati <= 25:
        return lati * 0.87
    
    elif lati <= 50:
        return lati * 0.76 + 3.1
    
    else:  # latitude > 50 deg
        return 40

def automatic_dataset(lati, long, year):
    """
    Returns the optimal dataset based on location and year.
    CM-SAF SARAH returned if location within "Europe/NA square"
    and year between 2000-2015.
    
    "Europe/North Africa square" (lat,lon):
        
        (65,-11)        (65,44)
        
        
        (24,-11)        (24,44)

    Parameters
    ----------
    lati : flaot
        Location latitude.
    long : flaot
        Location longitude.
    year : int
        Data year.

    Returns
    -------
    str
        Optimal dataset for given location and year.

    """
    if (lati <= 65 and lati >= 24) and (long <= 44 and long >= -11) and (year <= 2015 and year >= 2000):
        return "sarah"
    
    else:
        return "merra2"