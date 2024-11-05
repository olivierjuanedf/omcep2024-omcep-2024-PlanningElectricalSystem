import data_reader
import numpy as np
import pandas as pd
import os
import datetime

########################## For the numerical scheme ##########################

#Starting time of the optimization
t_0 = datetime.datetime(year = 2030, month = 1, day = 7, hour = 7, minute = 0)

#Time horizon 
T = 12 #h


#Choose the number n_x of discrete space steps and 
n_x=10
n_t= T*50    #we advice 50*T


delta_t = T/n_t
delta_x = 1/n_x
ratio=(delta_t)/(delta_x)
print(f'n_t = {n_t}, delta_t = {delta_t}, delta_x = {delta_x}, ratio = { ratio }')

d_t = np.linspace(0.,T,n_t+1)
d_x = np.linspace(0.,1,n_x+1)

i_t = list(range(n_t+1))
i_x = list(range(n_x+1))



########################## Parameters of the model ########################## 

I = [0,1] # choose the possible charging states
v2g = True
p_max =10 #kW, pmax of the plugg. Same value for V1G and V2G

if v2g: 
    I.append(-1) #we add the V2G mode

static_data_path =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'input','aggregate_ev_static_params.csv')
number_EV,battery_capacity = data_reader.read_capacity_data(v2g = v2g, file_path=static_data_path)
#battery_capacity = 80 #kWh
#number_EV = 10000


def gen_init_distrib():  
    # Returns the initial distribution

    m_0 = { i :  np.array([0.0 for _ in i_x]) for  i in I }

    # Be careful of the discrete states of your model. If there is a source term, you have to consider the fact that there is a mass 0 for some modes. 
    
    m_0[0][0] = 1 #/delta_x

    return m_0

m_0 = gen_init_distrib()


########################## Define all the useful functionals related to the model  ##########################


########################## Define the charging speeds ##########################

def b(i,l): 

    coef = p_max/battery_capacity
    s = l/n_x  
    if i==0: # EV not charging
        return .0
    elif i==1:  # EV charging
        return coef if s<=.8 else  coef*(1-s)/(1-0.8)
    elif i == -1: 
        return -coef if s>=.8 else -coef*s/0.8

    
########################## Define the local costs ##########################


def c(k,i,l):
    t_1 = 8
    t_2 = 12
    t_3 = 17
    t_4 = 20

    off_peak_price = 0.1  #price for charging during off-peak hours : 0.1euro/kWh
    peak_price = 0.3  #price for charging during peak hours : 0.3euro/kWh
    
    t = delta_t * k 

    if i==0:
        return .0 
    
    elif i==1 or i==-1: 
        if (0.<=t<=t_1) or (t_2<= t <= t_3) or (t_4 <= t) :
            return peak_price *battery_capacity*b(i,l)    
        else :
            return off_peak_price  *battery_capacity*b(i,l)    
 
    return .0 


#Define the terminal cost g:
def g(i,s):
    s_p=s/n_x
    c_1 = 75
    c_2  = 0.7
    return c_1*max(0,c_2-s_p)**2


#Define L to penalize high transitions values:

c_3 = 5  #constant for affecting the transitions costs

def L(x):
    if x==0: 
        return 0.0
    elif x>0:
        return c_3 * 0.5 * x**2
    else:
        return np.Inf

    
#Evaluate the hamiltonian 
def H(x):
    if x >= 0 : 
        return (1/c_3)*0.5*x**2
    else:
        return 0.0
    



########################## For the mean field model ##########################

signal_data_path =  os.path.join(os.path.dirname(os.path.abspath(__file__)),'input','charging_profiles_2030-1-7.csv')
signal = data_reader.read_signal(v2g = v2g, file_path=signal_data_path) 
#signal_dict gives the average consumption per EV !
signal_dict = {t :signal[signal['time'] == t_0 + datetime.timedelta(hours=t)]['power'].iloc[0] / number_EV for t in range(T+2)}

def p(i,l):
    return battery_capacity*b(i,l)  

#Target signal for 1 EV
def r(t):
    """
    Linear interpolation of signal
    """
    #return 1*(1-np.cos(3*t*2*np.pi/T))+0.5*(1-np.cos(6*t*2*np.pi/T))+0.25*(1-np.cos(12*t*2*np.pi/T)) + -(t/T)*(t/T-1)*8

    previous_conso = signal_dict[int(t)]
    next_conso = signal_dict[int(t)+1]
    interpolation = previous_conso + (t-int(t))*(next_conso-previous_conso)
    return interpolation

    


#Signal tracking penalization function
c_4 = 5
def phi(r,x):
    return 0.5*c_4*(r - x)**2


def grad_phi(r,x):  
    return -c_4*(r-x)


def perspective(w,m):
         
    if m>0 and w>=0 : 
        return L(w/m )*m 
    elif m==0 and w==0 :
        return 0.0
    else : 
        return np.Inf 