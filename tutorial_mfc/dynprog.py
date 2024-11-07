import numpy as np
from model import *
import sys

########################## HJB resolution with mean field_term ##########################

def hjb(m):

  
    ######### Initialization #########

    #Define the value dic u 

    u = { i : [[0.0 for _ in d_x] for _ in d_t ] for i in I }


    ######### Backward procedure #########

    #Data at final time T

    for i in I : 

        u[i][n_t]=[g(i,l) for l in i_x]
    
    
    
    #Approximate u at previous times
    
    for k in i_t[:-1][::-1]: #iterate over time 

        grad_compute = grad_phi(r(k*delta_t) , sum([ sum([p(i,l_prime)*m[i][k][l_prime]  for i in I]) for l_prime in i_x ]) )
        

        for i in I : #iterate over charging states
            
            for l in i_x: #iterate over space states 
                
                somme=sum([  H( u[i][k+1][l]-u[j][k+1][l]) for j in I ])

                grad = grad_compute*p(i,l)   
            
                
                if b(i,l)<0: #if the charging speed is negative
                    
                    if l==0:  #boundary condition
                        
                        u[i][k][l] = ( u[i][k+1][l]
                                        + delta_t*( c(k,i,l) + grad )
                                        - delta_t*somme
                                        )
                
                    else :
                        
                        u[i][k][l] = ( u[i][k+1][l]*(1+b(i,l)*(delta_t)/(delta_x))
                                        - u[i][k+1][l-1]*b(i,l)*(delta_t)/(delta_x)
                                        + delta_t*( c(k,i,l) + grad ) 
                                        - delta_t*somme
                                        )
            
                else:  #if the charging speed is non negative 
                    
                    if l==n_x: #boundary condition
                        
                        u[i][k][l] = ( u[i][k+1][l]
                                        + delta_t*( c(k,i,l) + grad ) 
                                        - delta_t*somme
                                        )
                    
                    else :
                        
                        u[i][k][l] = ( u[i][k+1][l]*(1-b(i,l)*(delta_t)/(delta_x))
                                        + u[i][k+1][l+1]*b(i,l)*(delta_t)/(delta_x)
                                        + delta_t*( c(k,i,l) + grad )
                                        - delta_t*somme
                                        )
    return u    


########################## Define the best response mapping ##########################

def v(u):

    #Define the optimal controls related to the problem:
    def alpha(i,j,k,l):
        if k==n_t:
            return 0.0
        else:
            return max(u[i][k+1][l]-u[j][k+1][l],0)/c_3

    #Create the dic of optimal controls    
    alphas =  { i :{j:  [ [ alpha(i,j, k, l) for l in i_x] for k in i_t ] for j in I} for i in I } 
    
    return alphas



########################## Define the forward equation ##########################

def f(v):

    #define a distribution satisfying the initial condition
    m = { i :  np.array([ np.array([0.0 for _ in i_x]) for _ in i_t]) for i in I }

    for i in I : 
        m[i][0] = m_0[i]


    ######### Forward procedure  #########

    for k in range(n_t):
        
        for i in I:
            
            for l in i_x : 

                if l==0:
                    
                    if b(i,l+1)<=0:
                        
                        m[i][k+1][l]  = (  m[i][k][l] * ( 1 + (delta_t/delta_x)*b(i,l) - sum( [ v[i][j][k][l]*delta_t for j in I  ]  )  )
                                       + sum( [ m[j][k][l]*v[j][i][k][l]*delta_t for j in I ]  )
                                       - (delta_t/delta_x)*b(i,l+1)*m[i][k][l+1]
                                       )
                        
                    else:
                        
                        m[i][k+1][l] = (  m[i][k][l] * ( 1 - (delta_t/delta_x)*b(i,l) - sum( [ v[i][j][k][l]*delta_t for j in I  ]   ) )
                                      + sum( [ m[j][k][l]*v[j][i][k][l]*delta_t for j in I ]  )
                                      )
                        
                elif l==n_x :
                    
                    if b(i,l-1)<0:                                               
                        m[i][k+1][l] = (  m[i][k][l] * ( 1 + (delta_t/delta_x)*b(i,l) - sum( [ v[i][j][k][l]*delta_t for j in I  ]  ) )
                                      + sum( [ m[j][k][l]*v[j][i][k][l]*delta_t for j in I ]  )
                        )
                        
                    else:
                        
                        m[i][k+1][l] = (  m[i][k][l]  * ( 1 - (delta_t/delta_x)*b(i,l) - sum( [ v[i][j][k][l]*delta_t for j in I  ]  ) )
                                      + sum( [ m[j][k][l]*v[j][i][k][l]*delta_t for j in I ]  )
                                      + (delta_t/delta_x)*b(i,l-1)*m[i][k][l-1]
                                      )
                
                else:
                    
                    if b(i,l)<=0:
                    
                        
                        m[i][k+1][l] = (  m[i][k][l] * ( 1 + (delta_t/delta_x)*b(i,l)  - sum( [ v[i][j][k][l]*delta_t for j in I  ]  ) )
                                      + sum( [ m[j][k][l]*v[j][i][k][l]*delta_t for j in I ]  )
                                      - (delta_t/delta_x)*b(i,l+1)*m[i][k][l+1]
                                      )
                    else:
                        
                        m[i][k+1][l] = (  m[i][k][l]  * ( 1 - (delta_t/delta_x)*b(i,l)  - sum( [ v[i][j][k][l]*delta_t for j in I  ]  ) )
                                      + sum( [ m[j][k][l]*v[j][i][k][l]*delta_t for j in I  ]  )
                                      + (delta_t/delta_x)*b(i,l-1)*m[i][k][l-1]
                                      )
                ###### pOUR dEbug ####
                if m[i][k+1][l]<0:
                        raise ValueError('Space and time step not adapted')
                       # print(f' negative distribution k={k} l={l} m[i][k+1][l]= {m[i][k][l]}')

    
    return m


########################## Benamou-Brenier transform ##########################

def chi(m,alphas):

    w =  { i : {j :  [ [ 0.0 for l in i_x] for k in i_t ] for j in I } for i in I}
    
    ######### Apply the change of variables, pointwise : w(k,i,j,l)=m(k,i,l)*alpha(k,i,j,l) #########

    for i in I :
        for j in I : 
            for k in i_t[:-1]:
                for l in i_x : 
                    w[i][j][k][l] = m[i][k][l] * alphas[i][j][k][l]
     
    return ( m , w )

def reconstruct_control(m,w):

    alpha =  { i : {j :  [ [ 0.0 for l in i_x] for k in i_t ] for j in I } for i in I}
    
    ######### Apply the change of variables, pointwise : w(k,i,j,l)=m(k,i,l)*alpha(k,i,j,l) #########

    for i in I :
        for j in I : 
            for k in i_t[:-1]:
                for l in i_x : 
                    if m[i][k][l] >1e-5:
                        
                        alpha[i][j][k][l] = w[i][j][k][l] / m[i][k][l]
                    else:
                        alpha[i][j][k][l] = 0
    return alpha


