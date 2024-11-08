import numpy as np
import matplotlib.pyplot as plt
from model import *
from gfw import *
from simulation_fleet import *



######## Question 1 #######
#### Influence of the parameters on the convergence of Frank Wolfe ######
run_gfw = data["run_gfw"]

if run_gfw :
    max_iteration = data["max_iteration"]
    acceleration = data["acceleration"] 
    if acceleration :
        (list_epsilon,rho,u)= gfw_accelerated(max_iteration )
    else :
        (list_epsilon,rho,u)=gfw(max_iteration )

    # Plot upper bound of the optimality gap
    plot_primal_gap(list_epsilon)
    plot_log_primal_gap(list_epsilon)

    # Estimation, save and plot of the consumption
    conso = build_conso_from_distribution(m = rho,nb_EV = number_EV)
    save_consumption(conso, t_0.strftime("%m_%d_%Y_%Hh%Mmin")+'_mean_field_conso.json')
    plot_consumption(m= rho, nb_EV  = number_EV , lab = 'MF consumption', title =t_0.strftime("%m_%d_%Y_%Hh%Mmin")+f' mean field consumption for {number_EV} EVs')

    # Save the control and the distribution computed by GFW Algorithm
    save_json(data = u, file_name = t_0.strftime("%m_%d_%Y_%Hh%Mmin")+'_control.json' )
    rho_to_save = {i: [list(rho[i][t]) for t in i_t ] for i in I}
    save_json(data = rho_to_save,file_name = t_0.strftime("%m_%d_%Y_%Hh%Mmin")+'_distribution.json' )

#### Question 2 ######

# n is the number of EVs to be controlled
n = data["nb_EV_for_implementation"] # variable number_EV is defined in model.py. 

#We load the control and the distribution computed by the GFW algorithm
u = load_control(t_0.strftime("%m_%d_%Y_%Hh%Mmin")+'_control.json')
rho = load_distribution( t_0.strftime("%m_%d_%Y_%Hh%Mmin")+'_distribution.json')

trajectories,empirical_distribution = build_trajectories_markov_chain(n, u )

plot_consumption( m = empirical_distribution, nb_EV  = n , lab = 'EV fleet consumption', title =t_0.strftime("%m_%d_%Y_%Hh%Mmin")+f' EV fleet consumption for {n} EVs')
plot_comparison_consumption(  m_1 = empirical_distribution, m_2= rho , nb_EV  = n , lab = ['EV fleet consumption','MF consumption'], title =t_0.strftime("%m_%d_%Y_%Hh%Mmin")+f' comparison consumption for {n} EVs')
conso_emp = build_conso_from_distribution(m =rho,nb_EV = number_EV)
save_consumption(conso_emp, t_0.strftime("%m_%d_%Y_%Hh%Mmin")+'_empirical_conso.json')

## Question 3

## Plot final level of batery ##
plot_initial_final_level_soc(trajectories,t_0.strftime("%m_%d_%Y_%Hh%Mmin")+'_level_battery_beginning_end_of_period')

