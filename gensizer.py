# -*- coding: utf-8 -*-
"""

    Generation Sizer for "Energy 4 Development" VIP
    
    Code by Alfredo Scalera (alfredo.scalera.2019@uni.strath.ac.uk)
    
    Based on MATLAB code by Steven Nolan ( ).

"""
"""
FUTURE WORK

- make plotting function external/isolated --> current one influences PSO perf
- create automatic hyperparameter method
- power demand can be any length but should really be limited to preset
  lengths - x years, x months, x days etc... all with hourly time steps.
  this way solar power can be matched. (talk to Scott & Mike about it)

"""

import random
import math

import matplotlib.pyplot as plt
import numpy as np


class Particle:
    
    # technical trackers
    fuel_used = 0
    Edump = 0
    
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
    
    def __init__(self,name,array_len):
        """
        Particle object used for PSO in GenSizer object.

        Parameters
        ----------
        name : str
            Name of particle.
        array_len : int
            Length of arrays dedicated to power generation and
            batteries. GenSizer object should provide this.

        """
        
        self.name = name
        
        self.Psol = [0] * array_len
        self.Pgen = [0] * array_len
        self.Ebatt = [0] * (array_len + 1)       # to avoid overshooting
        
        # random x, y, z coordinates
        self.pos = [random.randint(0, 500), random.randint(0, 500), random.randint(0, 500)]
        
        # initial velocity is zero in all directions
        self.vel = [0,0,0]
        
        self.gbest_value = 10**60
        self.pbest_value = 10**60
        self.cost = 10**60
        self.pbest_pos = self.pos.copy()
        
    def __str__(self):
        """
        Prints name, position, velocity and cost value of particle.
        Used for debugging purposes.

        Returns
        -------
        str
            String containing name, position, velocity,
            cost of particle.

        """
        
        return (self.name + ", Position: " + str(self.pos) + ", Velocity: "
                + str(self.vel) + ". Cost: " + str(self.cost))

    def updatePosition(self):
        """
        Updates posistion of particle based on velocity.
        Saves previous location for later use.

        """
        
        # save previous position
        self.prev_pos = self.pos.copy()
        
        self.pos[0] = self.pos[0] + self.vel[0]  # update x
        self.pos[1] = self.pos[1] + self.vel[1]  # update y
        self.pos[2] = self.pos[2] + self.vel[2]  # update z
        
    
class GenSizer:
    
    def __init__(self, swarm_size, power_demand, psol_unit,
                 sol_cost, batt_cost, gen_cost, fuel_cost, # costs
                 batt_Wh_max_unit, batt_Wh_min_unit,       # battery parameters
                 gen_max_power_out, gen_fuel_req,        # generator parameters
                 max_off_hours, min_autonomy_days):
        """
        Establishes optimal combination of PV array size, number of 
        batteries, and number of generators needed to meet power
        mini-grid's power demand with lowest cost. Uses particle swarm
        optimisation to do so.

        Parameters
        ----------
        swarm_size : int
            Number of particles used in PSO.
        power_demand : array-like
            Array containing yearly mini-grid power demand.
            Hourly timestep (length should be 8760).
        psol_unit : array-like
            Array containing power provided by single PV panel.
        sol_cost : float
            Cost of single PV panel.
        batt_cost : float
            Cost of single battery.
        gen_cost : float
            Cost of single diesel generator.
        fuel_cost : float
            Cost of fuel per liter.
        batt_Wh_max_unit : float
            Battery maximum Wh capacity.
        batt_Wh_min_unit : float
            Battery minimum Wh capacity (lowest it can go).
        gen_max_power_out : float
            Maximum power output of generator in Watts.
        gen_fuel_req : float
            Fuel requirement in liter per hour of generation
            at max power.
        max_off_hours : int
            Maximum hours in a year the grid can be offline for.
            More will decrease cost.
        min_autonomy_days : int
            Number of autonomy days required for grid. More will
            increase cost.

        """

        self.swarm_size = int(swarm_size)
        self.Pdem = power_demand
        self.Psol_unit = psol_unit
        
        # component costs
        self.solCost = sol_cost
        self.battCost = batt_cost
        self.genCost = gen_cost
        self.fuelCost = fuel_cost
        
        # technical parameters
        self.EbattMax_unit = batt_Wh_max_unit
        self.EbattMin_unit = batt_Wh_min_unit
        self.Pgen_unit = gen_max_power_out
        self.fuelReq = gen_fuel_req
        
        # offline & days of autonomy
        self.timebreakerMax = max_off_hours
        self.autonomDaysMin = min_autonomy_days
        
        # generate swarm
        self.swarm = []
        array_len = len(power_demand)
        for i in range(self.swarm_size):
            name = "Particle " + str(i)
            self.swarm.append(Particle(name, array_len))
        
        self.Pdem = power_demand
        self.Psol_unit = psol_unit
        
        # naughty list
        self.invalid_particles = []
        
    def _test_constraints(self):
        """
        Checks which particles do not meet power demand. Adds invalid
        particles to "naughty" list so they can be dealt with later.

        """
        
        self.invalid_particles.clear()
        
        for p in self.swarm:    # p = particle
            
            p.prev_fuel = p.fuel_used
            p.fuel_used = 0
        
            # check if particle has negative values
            if p.pos[0] < 0 or p.pos[1] < 0 or p.pos[2] < 0:
                self.invalid_particles.append(p)
                continue
            
            p.Pgen = [0] * len(self.Pdem)
            p.Ebatt = [0] * (len(self.Pdem) + 1)  # +1 avoids overshoot
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
            P1day = sum(self.Pdem[0:24])
            
            # check if configuration can sustain microgrid for set days
            p.autonomDays = Nb*(self.EbattMax_unit - self.EbattMin_unit)/P1day
            if p.autonomDays < self.autonomDaysMin:
                self.invalid_particles.append(p)
                continue
            
            timebreaker = 0
            
            for t in range(len(self.Pdem)):
                
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

    def _delete_invalid(self):
        """
        Deletes invalid particles. Only used in initialisation phase
        of particle swarm optimisation.

        """
        
        for p in self.invalid_particles:
            self.swarm.remove(p)
        
    def _update_pos_all(self):
        """
        Updates position of all particles within swarm.

        """
        
        for p in self.swarm:
            p.updatePosition()
    
    def _reset_invalid(self):
        """
        Resets to last valid position all particles in "naughty" list.

        """
        
        for p in self.swarm:
            if p in self.invalid_particles:
                p.pos = p.prev_pos.copy()
                p.vel = [0, 0, 0]
                p.fuel_used = p.prev_fuel
    
    def _fitness_all(self):
        """
        Evaluates cost of each particle within swarm, updates global
        best value and position, updates particle's best value and
        position.

        """
        
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
            p.gbest_pos = gbest_pos#.copy()
            p.gbest_value = gbest
            
    def _update_vel_all(self, current_iter):
        """
        Updates velocity for all particles in swarm.

        Parameters
        ----------
        current_iter : int
            Number of PSO loop iteration. Used for dynamic
            intertia (w), self-confidence (c1) and conformity (c2)
            hyperparameters.

        """
        
        for p in self.swarm:
            
            # PSO parameters
                # w inertia
                # c1 self confidence, c2 social conformity
                # r1, r2 random factors
            
            # LINEAR
            # w = 0.5*(self.max_iter - current_iter)/(self.max_iter) + 0.4
            
            # PARA UP
            # w = (0.5 * ((current_iter - self.max_iter)**2 / self.max_iter**2)
            #      + 0.4)
            
            # PARA DOWN
            w = 0.9 - 0.5 * (current_iter**2 / self.max_iter**2)
            
            # LIENAR C1 & C2
            # c1 = -3*(current_iter / self.max_iter) + 3.5
            # c2 = 3*(current_iter / self.max_iter) + 0.5
            
            c1 = 2.05  # particle's self confidence
            c2 = 2.05  # particle's conformity
            r1 = random.random()
            r2 = random.random()
            
            pbest = p.pbest_pos.copy()
            gbest = p.gbest_pos.copy()

            p.vel[0] = math.floor(w*p.vel[0] + c1*r1*(pbest[0]-p.pos[0]) 
                                  + c2*r2*(gbest[0]-p.pos[0]))
            p.vel[1] = math.floor(w*p.vel[1] + c1*r1*(pbest[1]-p.pos[1]) 
                                  + c2*r2*(gbest[1]-p.pos[1]))
            p.vel[2] = math.floor(w*p.vel[2] + c1*r1*(pbest[2]-p.pos[2]) 
                                  + c2*r2*(gbest[2]-p.pos[2]))
    
    def _check_converge(self):
        """
        Checks if swarm has converged before maximum number of
        itarations met.

        """

        positions = [particle.pos for particle in self.swarm]
        
        velocities = [particle.vel for particle in self.swarm]
        
        # self.converged is true if:
        #   all the particles have 0 velocity in all directions
        #   (and condition to check for empty list)
        #   all particles are in the same position
        self.converged = ((velocities.count([0,0,0]) == len(velocities)) 
                         and (positions.count(positions[0]) == len(positions)))
        
        # cleanup
        del velocities
        del positions
        
    def _animate(self,iteration_number):
        """
        Creates 3D scatter plot animation of swarm. Hinders performance
        and works best with IDE that have inline plotting.
        (for example Spyder, Jupyter Notebooks)

        Parameters
        ----------
        iteration_number : int
            PSO loop iteration number.

        """
        
        self.fig = plt.figure()
        ax = self.fig.add_subplot(projection = "3d")
        x, y, z = [], [], []
        for p in self.swarm:
            x.append(p.pos[0])
            y.append(p.pos[1])
            z.append(p.pos[2])
        ax.scatter(x,y,z, marker="o", 
                   c=random.sample([x for x in range(self.swarm_size)],len(x)),
                   cmap="Set2")
        
        ax.set_xlabel("Solar Panels")
        ax.set_ylabel("Batteries")
        ax.set_zlabel("Generators")
        
        xloc = plt.MaxNLocator(3)
        ax.xaxis.set_major_locator(xloc)
        
        ax.view_init(20,50)
        
        plt.show()
        
        del self.fig
    
    def optimise(self, max_iter, final_plot=False, animate=False):
        """
        Optimises generation mix by applying PSO.

        Parameters
        ----------
        max_iter : int
            maximum number of iterations.
        final_plot : bool, optional
            Plots power demand (W), solar power (W),
            battery energy (Wh) and generator power (W)
            against time (h). The default is False.
        animate : bool, optional
            Animate swarm while optimising. The default is False.

        """
        
        # used for inertia correction (w) in velocity update
        self.max_iter = max_iter
        
        # remove particles outside feasible region
        self._test_constraints()
        self._delete_invalid()
        
        # PSO loop
        self.converged = False
        i = 0
        while (i < max_iter) and (self.converged == False):
            
            if i % 1 == 0:
                print("\n\niteration:",i+1)
                
                print("\nPos:",self.swarm[0].pos)
                print("Cost:",self.swarm[0].cost)
                print("Vel:",self.swarm[0].vel)
                print("FUEL:", self.swarm[0].fuel_used)
                
                print("\nPbest:",self.swarm[0].pbest_pos)
                print("Pb cost:",self.swarm[0].pbest_value)
                
                print("\nGbest:",self.swarm[0].gbest_pos)
                print("Gb cost:",self.swarm[0].gbest_value)
            
            self._update_pos_all()
            self._test_constraints()
            self._reset_invalid()
            self._fitness_all()
            self._update_vel_all(i)  # iter number passed to adjust inertia
            self._check_converge()
            
            if animate == True: 
                self._animate(i)

            
            i += 1
        
        self.total_cost = self.swarm[0].cost
        
        # displaying results in console
        print("\nSolar Panels:\t\t", self.swarm[0].pos[0])
        print("Batteries:\t\t", self.swarm[0].pos[1])
        print("Generators:\t\t", self.swarm[0].pos[2])
        print("Fuel used:\t\t", self.swarm[0].fuel_used)
        print("Cost:\t\t\t",round(self.swarm[0].cost,2))
        print("Days of Autonomy:\t",round(self.swarm[0].autonomDays,2))
        
        # !!! final plotting -- turn into proper method for final version
        if final_plot == True:
            
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
            plt.plot(t, [self.swarm[0].pos[1] * self.EbattMax_unit]*8760,
                     label="Max. capacity")   # line showing max capacity
            plt.plot(t, [self.swarm[0].pos[1] * self.EbattMin_unit]*8760,
                     label="Min. capacity")   # line showing min capacity
            plt.xlabel("Time (h)")
            plt.ylabel("Energy (Wh)")
            plt.xlim(0,xmax)      # only show first 24hrs
            plt.yticks(np.linspace(0,self.swarm[0].pos[1] * self.EbattMax_unit,
                                   num=7))
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.075), 
                       shadow=True, ncol = 3)
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
        # update pbest & gbest
        # update velocity