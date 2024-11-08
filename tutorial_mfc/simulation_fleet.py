import numpy as np
import json
import matplotlib.pyplot as plt
import os
from model import *

def print_progress_bar(iteration, total, length=50):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\rProgress: |{bar}| {percent}% Complete', end='\r')
    if iteration == total:
        print()


def build_trajectories_markov_chain(nb: int, alpha: dict)-> (dict,dict) :

    print("## Simulation of the N EVs Markov Chains : can take times for large number of EVs ## ")
    
    initial_state = {}
    proba_for_initial_state = {(i,l): m_0[i][l] for i in I for l in i_x}
    for ev in range(nb):
        int_output = np.random.choice(a = np.arange(len( proba_for_initial_state.keys())), p = list(proba_for_initial_state.values()))
        key_state = list(proba_for_initial_state.keys())[int_output]
        initial_state[ev] = key_state


    dict_trajectories = {n : {0:initial_state[n]} for n in range(nb)}
    empirical_distribution =  { i :  np.array([ np.array([0.0 for _ in i_x]) for _ in i_t]) for i in I }
    
    for ev in range(nb):
        mode = initial_state[ev][0]
        soc = int(initial_state[ev][1]/delta_x)
        empirical_distribution[mode][0][soc] +=1/nb
        for t in i_t[1:]:
            proba = {}
            proba = {(j,soc) : delta_t*alpha[mode][j][t-1][soc] for j in I if j != mode }
            if b(mode, soc)>=0:
                proba[(mode,soc+1)] = delta_t/delta_x *  b(mode, soc)
            else :
                proba[(mode,soc-1)] = -delta_t/delta_x *  b(mode, soc)

            proba[(mode,soc)] = 1 - sum(proba.values())
            int_output = np.random.choice(a = np.arange(len( proba.keys())), p = list(proba.values()))
            next_state = list(proba.keys())[int_output]
            dict_trajectories[ev][t] =  next_state
            mode = next_state[0]
            soc = next_state[1]
            empirical_distribution[mode][t][soc] +=1/nb
        print_progress_bar(ev + 1, nb)



    return dict_trajectories,empirical_distribution


def plot_initial_final_level_soc(dict_trajectories :dict, filename):

    list_initial_soc = [dict_trajectories[ev][i_t[0]][1]*delta_x for ev in dict_trajectories.keys()]
    list_final_soc = [dict_trajectories[ev][i_t[-1]][1]*delta_x for ev in dict_trajectories.keys()]
    plt.hist( bins = d_x,x =  list_initial_soc, density = True, label = 'initial SoC')
    plt.hist( x =  list_final_soc, density = True, label = 'final SoC')

    plt.xlabel('SoC')
    plt.ylabel('Density')
    plt.legend(loc='center right')
    plt.grid()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','output','mfc','figures',filename+'.png' )
    plt.savefig(path)
    plt.show()
    plt.close()
    return None

def build_conso_from_distribution(m: dict,nb_EV: int)->list:

    return [sum([sum([(p(i, l) *m[i][t][l]*nb_EV ) for l in i_x]) for i in I]) for t in i_t]

def plot_consumption(m: dict,nb_EV: int, lab: str, title : str):

    conso =   build_conso_from_distribution(m, nb_EV)
    ref=[]
    for t in i_t : 
        t=delta_t*t
        ref.append(r(t)*nb_EV)

    plt.figure(figsize=(8, 5))
    new_x_axis = np.linspace(0, T, len(i_t))
    # Plot of the average consumption profile 'CP'
    plt.plot(new_x_axis, conso, alpha=0.5, color='green',label=lab)
    plt.plot(new_x_axis, ref, alpha=0.5, color='red',label='Target conso')
    plt.xlabel('Time (h)')
    plt.ylabel('Power (kW)')
    plt.title(title)
    plt.legend(loc='center right')
    plt.grid()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','output','mfc','figures',title+'.png' )
    plt.savefig(path)
    plt.show()
    plt.close()


def plot_comparison_consumption  (m_1 : dict , m_2 :dict,  nb_EV : int  , lab : list , title : str):
   
    conso_1 =   build_conso_from_distribution(m_1, nb_EV)
    conso_2 =   build_conso_from_distribution(m_2, nb_EV)

    ref=[]
    for t in i_t : 
        t=delta_t*t
        ref.append(r(t)*nb_EV)

    plt.figure(figsize=(8, 5))
    new_x_axis = np.linspace(0, T, len(i_t))
    # Plot of the average consumption profile 'CP'
    plt.plot(new_x_axis, conso_1, alpha=0.5, color='green',label=lab[0])
    plt.plot(new_x_axis, conso_2, alpha=0.5, color='blue',label=lab[1])
    plt.plot(new_x_axis, ref, alpha=0.5, color='red',label='Target conso')
    plt.xlabel('Time (h)')
    plt.ylabel('Power (kW)')
    plt.title(title)
    plt.legend(loc='center right')
    plt.grid()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','output','mfc','figures',title+'.png' )
    plt.savefig(path)
    plt.show()
    plt.close()


def save_consumption(conso : list, filename: str):

    dict_conso = {(t_0+datetime.timedelta(hours = t)*delta_t).strftime("%m/%d/%Y, %H:%M:%S") : conso[t] for t in range(len(conso))}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','output','mfc','data',filename )
    with open(path, 'w') as f:
        json.dump(dict_conso, f)
    return None

def save_json(data ,file_name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','output','mfc','data',file_name )
    with open(path, 'w') as f:
        json.dump(data, f)
    return None


def load_control(file_name):
    
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','output','mfc','data',file_name )
    with open(path, 'r') as f:
        u_str = json.load(f)

    u = {}
    for k1 in u_str.keys():
        u[int(k1)] = {}
        for k2 in u_str[k1].keys():
            u[int(k1)][int(k2)] = u_str[k1][k2]

    return u

def load_distribution( file_name) :
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','output','mfc','data',file_name )
    with open(path, 'r') as f:
        rho_str = json.load(f)
        
    rho = {}
    for k in rho_str.keys():
        rho[int(k)] = rho_str[k]
       
    return rho
