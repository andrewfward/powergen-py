# -*- coding: utf-8 -*-

from PVOutput import pv_power_output
from genSizer import *

pv_unit = pv_output(34.125, 39.814, 2015, 1.0, system_loss=0.1)

g = genSizer(50, pv_unit)
g.mainLoop(69, animate=False, plot=False)