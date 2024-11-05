import numpy as np
import matplotlib.pyplot as plt
import json
from scipy import optimize
from model import *
from dynprog import *
import sys


########################## Cost functions of the optimization problem ##########################

def mean_conso(k,m_p):
    return sum([   sum([ p(i,l)*m_p[i][k][l]  for l in i_x ]) for i in I ]) 


def linearized_mfc(k,m_p,m):  

    return sum(    [  sum(     [ grad_phi(r(k*delta_t) , mean_conso(k,m_p) )*p(i,l)*m[i][k][l]    for l in i_x    ])   for i in I ])
    


def int_2(k,m,w):
    return sum(    [   sum(    [ c(k,i,l)*m[i][k][l] + sum(   [perspective( w[i][j][k][l] , m[i][k][l]  ) for j in I ]   ) for l in i_x]  )  for i in I  ] )
    


def cost(m_p,m,w,string):

    running_cost= delta_t * sum(    [  int_2(k,m,w)  for k in i_t[:-1]   ]  )
    terminal_cost= sum(  [ sum( [g(i,l)*m[i][n_t][l] for l in i_x] ) for i in I  ]  )

    mft = 0

    if string == 'linear':

        
        mft = delta_t*sum(  [   linearized_mfc(k,m_p,m) for k in i_t[:-1]   ] )    
    else :

        mft = delta_t * sum(   [ phi(r(k*delta_t), mean_conso(k,m)) for k in i_t[:-1] ])


    return (running_cost+terminal_cost+mft,1)


    

def opv(m,w):   #returns the mean field cost for measure m and control w
    return cost(m_0,m,w,'')[0]


def lopv(m_p,m,w):   #returns the linearized mean field cost around measure m_p for measure m and control w 
    return cost(m_p,m,w,'linear')[0]


########################## Define the best response (BR for short) mapping ##########################



def br(m_p,bool):
    u_local=hjb(m_p)
    alphas_local=v(u_local)
    m_local=f(alphas_local)
    if bool==True :
        val=sum([ sum([ u_local[i][0][l]*m_0[i][l] for l in i_x  ]) for i in I])
        return ( chi( m_local , alphas_local ) , val  , alphas_local)
    
    return ( chi( m_local , alphas_local ) , .0 , alphas_local )



##### Linesearch #######

def  convex_combination_cost(step, m_bar,w_bar,m,w):

    m_combination = { i : np.array([ np.array([ (1-step)*m[i][k][l]+step*m_bar[i][k][l] for l in i_x  ])  for k in i_t ]) for i in I }
    w_combination = { i : { j : [ [ (1-step)*w[i][j][k][l]+step*w_bar[i][j][k][l] for l in i_x ] for k in i_t ] for j in I } for i in I } 
    

    return opv(m_combination,w_combination)

def  optimal_step_linesearch(m_bar,w_bar,m,w):

    opt = optimize.minimize_scalar(lambda step : convex_combination_cost(step, m_bar,w_bar,m,w), bounds = (0,1))
    step = opt.x
    return step



####### FW Algorithms ############

def gfw(nb_max_iter): # GFW algorithm 


    u_input = { i : {j :  [ [ 0.0 for l in i_x] for k in i_t ] for j in I } for i in I}
    rho_input = f(u_input)
    input = chi ( rho_input , u_input )
    vop=opv(input[0],input[1])
    print('At initialization problem\'s value is:'  , vop)
   
    ######### Initialization #########
   
    [(rho_k,w_k),(rho_bar_k,w_bar_k)] = [br(input[0],False)[0]]*2
    
    #Step initialization 
    step = 1.0
    
    #primal gap
    list_epsilon = []  

    ######### Loop #########
    for k in range(1,nb_max_iter+1):

        #########Step 1 : resolution of the partial linearized problem#########
        ((rho_bar_k,w_bar_k),mean_criterion,alpha_bar)=br(rho_k,True)
        epsilon_k = compute_estimation_primal_gap(rho_k,w_k,rho_bar_k,w_bar_k,rho_k)
        list_epsilon.append(epsilon_k)

        
        #########Step 2 : update #########

        #For non-accelerated scheme
        step = 2/(2+k)

        #########Update the distribution  #########
        rho_k = { i : np.array([ np.array([ (1-step)*rho_k[i][t][l]+step*rho_bar_k[i][t][l] for l in i_x  ])  for t in i_t ]) for i in I }
        
        ######### Update the control #########
        w_k =  { i : { j : [ [ (1-step)*w_k[i][j][t][l]+step*w_bar_k[i][j][t][l] for l in i_x ] for t in i_t ] for j in I } for i in I } 

    
        #To print all details of the iteration:
        print(f'k={k} \\ problem\'s value = { opv(rho_k,w_k) } \\ optimality gap = {epsilon_k} \\ step : {step} ' )
    
    u_k = reconstruct_control( rho_k , w_k)
    return (list_epsilon , rho_k , u_k)






def gfw_accelerated(nb_max_iter : int): # GFW algorithm 

    ######### Initialization #########
    u_input = { i : {j :  [ [ 0.0 for l in i_x] for k in i_t ] for j in I } for i in I}
    rho_input = f(u_input)
    input = chi ( rho_input , u_input )
    vop=opv(input[0],input[1])
    print('At initialization problem\'s value is:'  , vop)
      
    [(rho_k,w_k),(rho_bar_k,w_bar_k)] = [br(input[0],False)[0]]*2
    
    #Step initialization 
    step = 1.0
    
    #optimality gap
    list_epsilon = []   

    ######### Loop #########
    for k in range(1,nb_max_iter+1):

        #########Step 1 : resolution of the partial linearized problem#########
        ((rho_bar_k,w_bar_k),mean_criterion,alpha_bar)=br(rho_k,True)
        
        
        #########Step 2 : update #########

        
        #For accelerated
        epsilon_k = compute_estimation_primal_gap(rho_k,w_k,rho_bar_k,w_bar_k, rho_k)
        (a_cst,b_cst) =  ( cost(rho_k,rho_bar_k,w_bar_k,'')[0] - cost(rho_k,rho_k,w_k,'')[0] + epsilon_k , -epsilon_k )
        step=quadratic(a_cst,b_cst)

        #step = optimal_step_linesearch(rho_bar_k,w_bar_k,m,w)


        #########Update the distribution  #########
        rho_k = { i : np.array([ np.array([ (1-step)*rho_k[i][t][l]+step*rho_bar_k[i][t][l] for l in i_x  ])  for t in i_t ]) for i in I }
        
        ######### Update the control #########
        w_k =  { i : { j : [ [ (1-step)*w_k[i][j][t][l]+step*w_bar_k[i][j][t][l] for l in i_x ] for t in i_t ] for j in I } for i in I } 


        #To print all details of the iteration:
        list_epsilon.append(epsilon_k)
        print(f'k={k} \\ problem\'s value = { opv(rho_k,w_k) } \\ optimality gap = {epsilon_k} \\ step : {step} ' )


    u_k = reconstruct_control( rho_k , w_k)
    return (list_epsilon , rho_k , u_k)

def quadratic(a,b): #useful for the accelerated version of GFW
    coeff=-b/(2*a)
    return 0.0 if coeff <=0 else (1.0 if coeff>=1 else coeff) 


def  compute_estimation_primal_gap(m,w,rho_bar_k,w_bar,previous_dist):

        v1 = lopv(previous_dist,rho_bar_k,w_bar)
        v2 = lopv(previous_dist,m,w)
        
        return  v2 - v1

def plot_primal_gap(list_gap : list):

    plt.plot(list_gap, label = 'upper bound primal gap')
    plt.xlabel('Iterations')
    plt.legend(loc='center right')
    plt.grid()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'output','upper_bound_primal_gap.png' )
    plt.savefig(path)
    plt.show()
    return None

def plot_log_primal_gap(list_gap : list):

    log_x_axis = [np.log(k) for k in range(1,len(list_gap)+1)]
    log_gap = [np.log(gap) for gap in list_gap]
    plt.plot(log_x_axis, log_gap, label = 'log upper bound primal gap')
    plt.xlabel('log terations')
    plt.legend(loc='center right')
    plt.grid()
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'output','log_log_upper_bound_primal_gap.png' )
    plt.savefig(path)
    plt.show()
    return None

