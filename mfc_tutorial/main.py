import numpy as np
import matplotlib.pyplot as plt
from model import *
from gfw import *
from simulation_fleet import *



######## Question 1 #######
#### Influence of the parameters on the convergence of Frank Wolfe ######

max_iteration = 100
acceleration = False 
if acceleration :
    (list_epsilon,rho,u)= gfw_accelerated(max_iteration )
else :
     (list_epsilon,rho,u)=gfw(max_iteration )

# Plot upper bound of the optimality gap
plot_primal_gap(list_epsilon)
plot_log_primal_gap(list_epsilon)

# Estimation, save and plot of the consumption
conso = build_conso_from_distribution(m = rho,nb_EV = number_EV)
save_consumption(conso, 'mean_field_conso.json')
plot_consumption(m= rho, nb_EV  = number_EV , lab = 'MF consumption', title =f'MF consumption for {number_EV} EVs')

#### Question 2 ######

# To plot individual trajectories
n = number_EV
trajectories,empirical_distribution = build_trajectories_markov_chain(n, u )

plot_consumption( m = empirical_distribution, nb_EV  = n , lab = 'EV fleet consumption', title =f'EV fleet consumption for {n} EVs')
plot_comparison_consumption(  m_1 = empirical_distribution, m_2= rho , nb_EV  = n , lab = ['EV fleet consumption','MF consumption'], title =f'comparison consumption for {n} EVs')
conso_emp = build_conso_from_distribution(m =rho,nb_EV = number_EV)
save_consumption(conso_emp, 'empirical_conso.json')



## Question 3

## Plot final level of batery ##
plot_initial_final_level_soc(trajectories,'level_battery_beginning_end_of_period')

