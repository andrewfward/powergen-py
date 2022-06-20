# -*- coding: utf-8 -*-

from PVOutput import *
from genSizer import *

pv_unit = pv_output(25, 7, 2013, 0.2, auto_dataset=True, auto_tilt=True)

g = genSizer(50, pv_unit)
g.optimise(200, animate=False, plot=False)

# dataset = automatic_dataset(24, -11, 2000)
# print(dataset)