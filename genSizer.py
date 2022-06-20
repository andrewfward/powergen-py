# -*- coding: utf-8 -*-
"""

    Generation Sizer for "Energy 4 Development" VIP
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    Based on MATLAB code by Steven Nolan ( )

"""

import random, os, time
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

random.seed(19)      # rng

#-----FUNCTIONS--------------------------------------------------------------------------#

# MIGHT NEED TO CHANGE
# gets the data excel file name (assuming one excel file in folder)
def excelFileName():
    for folder, sub_folder, files in os.walk(os.getcwd()):
        for f in files:
            f_extension = os.path.splitext(f)[1]
            if f_extension in [".xlsx",".xls"]:
                return f
                break
            else:
                continue

#-----CLASSES----------------------------------------------------------------------------#

class Particle():
    
    # technical trackers
    Psol = [0]*8760
    Pgen = [0]*8760
    Ebatt = [0]*8761        # to avoid overshooting
    fuel_used = 0
    Edump = 0               # acts as inital value too
    
    # previous position placeholders
    prev_pos = []
    prev_fuel = 0
    
    # PSO variables
    pbest_pos = []
    pbest_value = 0
    gbest_pos = []
    gbest_value = 0
    
    cost = 0
    
    autonomDays = 0
    
    def __init__(self,name):
        self.name = name
        
        # random x, y, z coordinates
        self.pos = [random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)]
        
        # initial velocity is zero in all directions
        self.vel = [0,0,0]
        
        self.gbest_value = 10**60
        self.pbest_value = 10**60
        self.cost = 10**60
        self.pbest_pos = self.pos.copy()
        
    def __str__(self):
        return self.name + ", Position: " + str(self.pos) + ", Velocity: " + str(self.vel) + ". Cost: " + str(self.cost)

    def updatePosition(self):
        # save previous position
        self.prev_pos = self.pos.copy()
        
        self.pos[0] = self.pos[0] + self.vel[0]     # x
        self.pos[1] = self.pos[1] + self.vel[1]     # y
        self.pos[2] = self.pos[2] + self.vel[2]    # z
        
    
class genSizer():

    # cost of components    --> IDEALLY FROM EXTERNAL INPUT (user config)
    solCost = 150.98
    battCost = 301.71
    genCost = 320
    fuelCost = 0.32
    
    # technical parameters  --> IDEALLY FROM EXTERNAL INPUT (user config)
    EbattMax_unit = 2040
    EbattMin_unit = 408
    Pgen_unit = 750
    fuelReq = 1
    timebreakerMax = 0
    autonomDaysMin = 2
    
    def __init__(self, swarm_size, psol_unit):      # psol_unit is list
        self.swarm_size = swarm_size
        
        # generate swarm
        self.swarm = []
        for i in range(self.swarm_size):
            self.swarm.append(Particle("Particle " + str(i)))
        
        # retrieve power demand as list
        # !!! using automatic excel file detection, can change to manual
        df = pd.read_excel(excelFileName(), header=0, index_col=0)
        self.Pdem = df["Pdem"].values.tolist()
        self.Pdem = self.Pdem[0:8760]
        
        # retrieve single solar panel output power as list
        # self.Psol_unit = df["Psol"].values.tolist()
        # self.Psol_unit = self.Psol_unit[0:8760]
        self.Psol_unit = psol_unit
        
        # naughty list
        self.invalid_particles = []
        
    def testConstraints(self):
        
        self.invalid_particles.clear()
        
        for p in self.swarm:    # p = particle
            
            # check if particle has negative values
            if p.pos[0] < 0 or p.pos[1] < 0 or p.pos[2] < 0:
                self.invalid_particles.append(p)
                continue
            
            p.prev_fuel = p.fuel_used
            p.fuel_used = 0
            p.Pgen = [0]*8760
            p.Ebatt = [0]*8761
            p.Edump = 0
            
            Ns = p.pos[0]
            Nb = p.pos[1]
            Ng = p.pos[2]
            
            EbattMin = Nb * self.EbattMin_unit
            EbattMax = Nb * self.EbattMax_unit
            Pgen = Ng * self.Pgen_unit
            
            # assume batteries initally fully charged
            p.Ebatt[0] = EbattMax
            
            # avg power needed for 1 day
            #!!!
            # P1day = sum(self.Pdem) / (365)
            P1day = sum(self.Pdem[0:24])
            
            # check if configuration can sustain microgrid for set days
            p.autonomDays = Nb*(self.EbattMax_unit - self.EbattMin_unit)/P1day
            if p.autonomDays < self.autonomDaysMin:
                self.invalid_particles.append(p)
                continue
            
            timebreaker = 0
            
            for t in range(8760):
                
                p.Psol[t] = Ns * self.Psol_unit[t]
                
                # solar power matches demand
                p.Ebatt[t+1] = p.Ebatt[t]
                
                # # solar power exceeds demand, charge batteries
                # if p.Psol[t] >= self.Pdem[t]:
                    
                if p.Psol[t] > self.Pdem[t]:
                    Echarge = p.Psol[t] - self.Pdem[t]
                    #Echarge = Pcharge * 1      1Wh = 1W*1hr
                    
                    # energy charge exceeds max capacity, dump excess energy
                    if (p.Ebatt[t] + Echarge) > EbattMax:
                        p.Ebatt[t+1] = EbattMax
                        p.Edump += (p.Ebatt[t] + Echarge - EbattMax)
                
                    # energy charge below max capacity, charge battery
                    else:
                        p.Ebatt[t+1] = p.Ebatt[t] + Echarge
                
                # solar power below demand
                elif p.Psol[t] < self.Pdem[t]:
                    Edisch = self.Pdem[t] - p.Psol[t]
                    #Edisch = Pdisch * 1         1Wh = 1W*1hr
                    
                    # battery energy enough to meet demand
                    if (p.Ebatt[t] - Edisch) >= EbattMin:
                        p.Ebatt[t+1] = p.Ebatt[t] - Edisch
                    
                    # battery energy below demand, activate generators
                    else:
                        p.Ebatt[t+1] = p.Ebatt[t] + p.Psol[t] + Pgen - self.Pdem[t]
                        p.Pgen[t] = Pgen
                        p.fuel_used += (Ng * self.fuelReq)
                        
                        # generator power below demand
                        if p.Ebatt[t+1] < EbattMin:
                            timebreaker += 1
                            if timebreaker > self.timebreakerMax:
                                self.invalid_particles.append(p)
                                break
                        
                        # generator exceeds demand, charge batteries
                        elif p.Ebatt[t+1] > EbattMax:
                            p.Edump += (p.Ebatt[t+1] - EbattMax)
                            p.Ebatt[t+1] = EbattMax

    def deleteInvalid(self):
        for p in self.invalid_particles:
            self.swarm.remove(p)
    
    def updatePositionAll(self):
        for p in self.swarm:
            p.updatePosition()
    
    def resetInvalid(self):
        for p in self.swarm:
            if p in self.invalid_particles:
                p.pos = p.prev_pos
                p.vel = [0, 0, 0]
                p.fuel_used = p.prev_fuel
    
    def fitnessAll(self):
        # evaluate cost (obj function)
        for p in self.swarm:
            Ns = p.pos[0]
            Nb = p.pos[1]
            Ng = p.pos[2]
            
            p.cost = Ns*self.solCost*1.01 + Nb*3*self.battCost*1.01 + Ng*self.genCost*1.1*4.5 + 1.5*p.fuel_used*self.fuelCost
            
            # update particle pbest
            if p.cost < p.pbest_value:
                p.pbest_pos = p.pos.copy()
                p.pbest_value = p.cost
        
        # update gbest for all particles
        values = [] 
        for p in self.swarm:
            values.append(p.pbest_value)
        # find gbest and associated particle
        gbest = min(values)
        i = values.index(gbest)
        gbest_pos = self.swarm[i].pbest_pos.copy()
        # update gbest for each particle in swarm
        for p in self.swarm:
            p.gbest_pos = gbest_pos
            p.gbest_value = gbest
        
    def updateVelocityAll(self):
        for p in self.swarm:
            # PSO parameters
                # w inertia
                # c1 self confidence, c2 social conformity
                # r1, r2 random factors

            w = 0.5*(self.max_iter - self.i)/(self.max_iter) + 0.4        
            c1 = 2.03
            c2 = 2.03
            r1 = random.random()
            r2 = random.random()
            
            pbest = p.pbest_pos.copy()
            gbest = p.gbest_pos.copy()

            p.vel[0] = round(w*p.vel[0] + c1*r1*(pbest[0]-p.pos[0]) + c2*r2*(gbest[0]-p.pos[0]))
            p.vel[1] = round(w*p.vel[1] + c1*r1*(pbest[1]-p.pos[1]) + c2*r2*(gbest[1]-p.pos[1]))
            p.vel[2] = round(w*p.vel[2] + c1*r1*(pbest[2]-p.pos[2]) + c2*r2*(gbest[2]-p.pos[2]))
    
    def animate(self,iteration_number):
        self.fig = plt.figure()
        ax = self.fig.add_subplot(projection = "3d")
        x, y, z = [], [], []
        for p in self.swarm:
            x.append(p.pos[0])
            y.append(p.pos[1])
            z.append(p.pos[2])
        ax.scatter(x,y,z, marker="o", c=random.sample([x for x in range(self.swarm_size)],len(x)), cmap="Set2")
        
        ax.set_xlabel('Solar Panels')
        ax.set_ylabel('Batteries')
        ax.set_zlabel('Generators')
        
        xloc = plt.MaxNLocator(3)
        ax.xaxis.set_major_locator(xloc)
        
        ax.view_init(20,50)
        
        plt.show()
    
    def mainLoop(self, max_iter, plot=False, animate=False):
        
        # used for inertia correction (w) in velocity update
        self.max_iter = max_iter
        
        # remove particles outside feasible region
        self.testConstraints()
        self.deleteInvalid()
        
        # proper loop
        for i in range(max_iter):
            
            self.i = i
            
            if i % 1 == 0:
                print("\n\niteration:",i+1)
                
                print("\nPos:",self.swarm[0].pos)
                print("Cost:",self.swarm[0].cost)
                print("Vel:",self.swarm[0].vel)
                
                print("\nPbest:",self.swarm[0].pbest_pos)
                print("Pb cost:",self.swarm[0].pbest_value)
                
                print("\nGbest:",self.swarm[0].gbest_pos)
                print("Gb cost:",self.swarm[0].gbest_value)
            
            self.updatePositionAll()
            self.testConstraints()
            self.resetInvalid()
            self.fitnessAll()
            self.updateVelocityAll()
            if animate == True: 
                self.animate(i)
            
        # displaying results in consol
        print("\nSolar Panels:\t", self.swarm[0].pos[0])
        print("Batteries:\t\t", self.swarm[0].pos[1])
        print("Generators:\t\t", self.swarm[0].pos[2])
        print("Fuel used:\t\t", self.swarm[0].fuel_used)
        print("Cost:\t\t\t",self.swarm[0].cost)
        print("Days of Autonomy",self.swarm[0].autonomDays)
        
        if plot == True:
            
            t = [x for x in range(8760)]
            xmax = 72
            
            # power demand
            plt.figure()
            plt.plot(t, self.Pdem)
            plt.xlabel("Time (h)")
            plt.ylabel("Power Demand (W)")
            plt.xlim(0,xmax)      # only show first 24hrs
            # plt.ylim(0,1500)
            # plt.yticks([x for x in range(0,1500,250)])
            plt.ylim(0,max(self.Pdem)*(1.25))
            plt.yticks(np.linspace(0,max(self.Pdem)*1.25,num=6))
            plt.title("Power Demand vs Time (Initial 72 hours)")
            plt.show()
            
            # solar power
            plt.figure()
            plt.plot(t, self.swarm[0].Psol)
            plt.xlabel("Time (h)")
            plt.ylabel("Power (W)")
            plt.xlim(0,xmax)      # only show first 24hrs
            plt.title("Solar Power vs Time (Initial 72 hours)")
            plt.show()
            
            # energy batteries
            plt.figure()
            plt.plot(t, self.swarm[0].Ebatt[0:8760], label="Energy stored")
            plt.plot(t, [self.swarm[0].pos[1] * self.EbattMax_unit]*8760, label="Max. capacity")   # line showing max capacity
            plt.plot(t, [self.swarm[0].pos[1] * self.EbattMin_unit]*8760, label="Min. capacity")   # line showing min capacity
            plt.xlabel("Time (h)")
            plt.ylabel("Energy (Wh)")
            plt.xlim(0,xmax)      # only show first 24hrs
            plt.yticks(np.linspace(0,self.swarm[0].pos[1] * self.EbattMax_unit,num=7))
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.075), shadow=True, ncol = 3)
            plt.title("Stored Energy in Batteries vs Time (Initial 72 hours)")
            plt.show()
            
            # power generators
            plt.figure()
            plt.plot(t, self.swarm[0].Pgen)
            plt.xlabel("Time (h)")
            plt.ylabel("Power (W)")
            plt.xlim(0,xmax)      # only show first 24hrs
            plt.title("Generated Power vs Time (Initial 72 hours)")
            plt.show()
            
    # for max number iterations
        # update pos
        # for each particle in swarm
            # test constraints
        # invalid particles --> move back to prev pos and vel 0
        # for each particle
            # evaluate cost
        # update pbest
        # update gbest
        # update velocity
        

#-----LOGIC------------------------------------------------------------------------------#

# t1 = time.time()
# g = genSizer(50)
# g.mainLoop(69, animate=False, plot=False)
# t2 = time.time()
# print("\nelapsed time: ",t2-t1)