# -*- coding: utf-8 -*-
"""
    Demo for Renewables.ninja API integration (with generation sizer PSO)
"""
import random

import pvoutput as pv
import gensizer as gs

"""
Cost & technical parameters

    PV panel cost = £150.98 (per unit)
    battery cost = £301.71 (per unit)
    diesel generator cost = £320 (per unit)
    fuel cost = £0.32 (per Lt)
    
    PV panel capacity = 250 W
    maximum battery energy = 2040 Wh
    minimum battery energy = 408 Wh
    diesel generator rated power = 750 W
    fuel requirement = 1 Lt (per hour)
    requried days of autonomy = 2

    
"""
# parameters for generation sizer
solCost = 150.98
battCost = 301.71
genCost = 320
fuelCost = 0.32

pv_capacity = 250
EbattMax_unit = 2040
EbattMin_unit = 408
Pgen_unit = 750
fuelReq = 1
timebreakerMax = 0
autonomDaysMin = 2

# RNG seed
random.seed(420)

# coordinates for Jiboro in The Gambia
latitude = 13.17
longitude = -16.57

# power demand = 1000 W each hour for full year
power_demand = [1000]*8760

# retrieve estimated single PV panel output from RN

output_pv_unit = pv.pv_output(latitude, longitude, pv_capacity, year=2019,
                              auto_dataset=True, auto_tilt=True)

    # create generation sizer object with 50 particles
g = gs.GenSizer(50, power_demand, output_pv_unit, solCost, battCost, genCost,
                fuelCost, EbattMax_unit, EbattMin_unit, Pgen_unit, fuelReq,
                timebreakerMax, autonomDaysMin)

# optimise generation mix (animate=True for animation)
max_iterations = 300
g.optimise(max_iterations, animate=False, final_plot=False)