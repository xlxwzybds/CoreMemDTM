#
# This file is part of GDP.
# Copyright (C) 2022 Hai Wang and Qinhui Yang.
#
# GDP is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# GDP is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along
# with GDP. If not, see <https://www.gnu.org/licenses/>.
#

import numpy as np
## XJY add
from scipy.optimize import minimize
## XJY add

def gdp_map(A, temp_max, temp_amb, taskCoreRequirement, activeCores, availableCores, preferredCoresOrder, P_s):
    # The function to find the GDP optimized active core map
    # Inputs:
    # A: system thermal model matrix, usually A = B^T G^{-1} B according to the GDP paper
    # temp_max: temperature threshold scalar
    # temp_amb: ambient temperature scalar
    # taskCoreRequirement: the number of new active cores need to be mapped
    # activeCores: boolean vector of the existing active core map, indicating if each core is active (True) or inactive (False). If you want to override some existing active cores, set them to False.
    # availableCores: boolean vector of the current inactive cores that can be activated (active core candidates), indicating if each core can be activated (True) or cannot be activated (False)
    # preferredCoresOrder: the user specified activation order vector, -1 indicates the end of the preferred cores. These cores should be activated first (if available) before GDP computation. If user do not specify any activation order, simply set all elements to -1.
    # P_s: static power vector, each element is the static power value of each core, use an all zero vector if no static power
    # Output:
    # cores_to_activate: vector of the new active core indexes

    # total core number of the multi/many core system
    core_num = availableCores.shape[0]
    
    # find the user specified preferred cores that are still in available cores, they should be activated first without GDP computing
    inact_pref_cores = np.zeros(core_num) - 1 # initiate all elements to -1
    n_ipc = 0 # number of inactive preferred cores
    for core_id in preferredCoresOrder:
        if availableCores[core_id] == True and core_id != -1:
            inact_pref_cores[n_ipc] = core_id
            availableCores[core_id] = False
            activeCores[core_id] = True
            n_ipc = n_ipc+1

    # Initiate cores_to_activate using inact_pref_cores, becuase we need to activate the inactive preferred cores first. 
    cores_to_activate = inact_pref_cores[:taskCoreRequirement] # all the inactive preferred cores should be activated first

    # If taskCoreRequirement <= n_ipc, then we are simply done without GDP computation. Otherwise (if taskCoreRequirement > n_ipc), we need to determine the remaining active cores using GDP iterations.
    if taskCoreRequirement > n_ipc:
        # for 3D-DGP, Add something here 
        availableCores_new = np.pad(availableCores, (16, 0), 'constant', constant_values=False) # add for 3d-gdp
        availableBanks_new = np.pad(availableCores, (0, 16), 'constant', constant_values=False) # add for 3d-gdp
        A = np.atleast_2d(A[availableBanks_new][:,availableCores_new])
        P_s = P_s[availableCores_new] # for 3D_GDP

        # initiate GDP iterations
        T_s = A@P_s # static power's impact on temperature, should be substracted from T_th later
        T_th = np.full((core_num,), temp_max - temp_amb) - T_s # threshold temperature vector
        if np.sum(activeCores) > 0:
            Ai = np.atleast_2d(A[activeCores][:,activeCores])
            T_th_i = T_th[activeCores]
            Pi = np.linalg.solve(Ai, T_th_i) # power budget of the existing active cores
            T_rm = T_th[availableCores] - A[availableCores][:,activeCores]@Pi # temperature threshold headroom of the available cores (candidates) by substracting the existing active cores' thermal impact
        else: # when there is no existing active core and no user preferred core
            T_rm = T_th[availableCores]
        
        # for 3D-DGP, the matrix Aa should be changed here
        Aa = np.atleast_2d(A[availableCores][:,availableCores]) # orignal Code for DDR-gdp method
        #Aa = np.atleast_2d(A[availableBanks_new][:,availableCores_new])

        idx_available_cores = np.flatnonzero(availableCores) # original for ddr-gdp
        # idx_available_cores = np.flatnonzero(availableCores_new) # change for 3d-gdp
        for i in range(n_ipc, taskCoreRequirement):
            # find the core in available cores (candidates) which leads to the largest power budget (indicated by the largest inner product with T_rm)
            idx = 0
            for j in range(1,idx_available_cores.shape[0]): 
                if np.inner(Aa[:][j],T_rm) > np.inner(Aa[:][idx],T_rm):
                    idx = j
            # add the new active core (idx) to the exsiting active cores
            cores_to_activate[i] = idx_available_cores[idx] # add the new active core (idx) to the list of cores to activate as the final output
            availableCores[idx_available_cores[idx]] = False
            activeCores[idx_available_cores[idx]] = True
            Aa = np.atleast_2d(A[availableCores][:,availableCores]) # change for 3D-GDP Method
            idx_available_cores = np.flatnonzero(availableCores)
            
            # update T_rm
            Ai = np.atleast_2d(A[activeCores][:,activeCores]) 
            T_th_i = T_th[activeCores]
            Pi = np.linalg.solve(Ai, T_th_i)
            T_rm = T_th[availableCores] - A[availableCores][:,activeCores]@Pi

    print("the cores_to_activate is below ",cores_to_activate);
    return cores_to_activate

def gdp_power(A, core_map, temp_max, temp_amb, P_s, P_k, T_c, gdp_mode):
    # The function to compute the GDP power budget for a given active core map
    # Inputs:
    # A: system matrix, usually A = B^T G^{-1} B according to the GDP paper
    # core_map: boolean vector of the active core map, indicating if each core is active (True) or inactive (False)
    # temp_max: temperature threshold scalar
    # temp_amb: ambient temperature scalar
    # P_s: static power vector, each element is the static power value of each core, use an all zero vector if no static power
    # P_k: power vector of all cores at the previous step (assume current time is t, power budgeting/DVFS step is h, P_k is the power from time t-h to t, and we want to compute the power budget P for time t to t+h)
    # T_c: temperature vector of all cores at the current time (at time t in the example of P_k)
    # gdp_mode: 'steady' for steady state GDP and 'transient' for transient GDP
    # Output:
    # P: power budget of the active cores according to core_map

    # Compute the static power's impact on temperature. If the static power is assumed to be constant (such as in HotSniper), this impact is constant and actually can be pre-computed only once outside
    NUM = A.shape[0] / 2 ;
    ####################################
    ## 1.XJY change: cut P_s [32x1] to [16x1]
    ####################################
    #T_s = A@P_s  # static power's impact on temperature, should be substracted from T_th later
    P_s[:16] = 0  # static power of memroy bank , we set it to zero 
    #print('P_s is', P_s)
    T_s = A@P_s ; # dimension of T_s is [32x1]
    
    #print("the information of coremap is", core_map)
    # formulate the Ai matrix (a submatrix of A according to the active core mapping)
    ####################################
    ## 2.XJY change: 
    ####################################
    # Ai = np.atleast_2d(A[core_map][:,core_map])
    #
    bank_map     = np.pad(core_map, (0, 16), 'constant', constant_values=False)
    core_map_new = np.pad(core_map, (16, 0), 'constant', constant_values=False)
    #print('bank_map is', bank_map)
    #print('core_map_new is', core_map_new)
    Ai = np.atleast_2d(A[bank_map][:,:])
    Ac = np.atleast_2d(A[bank_map][:,core_map_new])

    A_tc = np.atleast_2d(A[core_map_new][:,:])              # Critical temperature of banks belows the Active_Core
    A_lc = np.atleast_2d(A[core_map_new][:,core_map_new])   # How activate Cores affect the temp of banks
    

    # do not change here !
    if gdp_mode == 'steady': # for steady state GDP
        T_th = np.full((Ai.shape[0],), temp_max - temp_amb) - T_s[core_map] # threshold temperature vector
    else: # for transient GDP
        #print("the shape of Matrix Ai is ",Ai.shape[0]);
        #print("the shape of Matrix Tc is ",T_c.shape[0]);
        #print("the shape of Matrix Tk is ",P_k.shape[0]);
        #print("the shape of Matrix Ts is ",T_s.shape[0]);
        ## change original 16 dimension to 32 , 16 cores + 16 banks
        # version_1 : original
        #       T_th = np.full((Ai.shape[0],), temp_max) - T_c[core_map] + Ai@(P_k[core_map]) - T_s[core_map]
        # version_2 : CoMeT DDR GDP INSERT
        #       core_map_new = np.pad(core_map, (0, 16), 'constant', constant_values=False)
        #       T_th = np.full((Ai.shape[0],), temp_max) - T_c[core_map_new] + Ai@(P_k[core_map_new]) - T_s[core_map]
        # version_3 : 3D_GDP
        #       np.full((Ai.shape[0],), temp_max) : dimemsion is [8x1]
        #       T_c[core_map_new] : current temperature of the activate cores. The critical component is Bank.
        #       Ai@P_K : 
        #       T_s[core_map_new] : static temperature of activate core
        #print('T_c is ',T_c[bank_map])
        #print('P_k is ',P_k)
        #print(Ai@P_k)
        ## 


        #T_th = np.full((Ai.shape[0],), temp_max) - T_c[bank_map] + Ac@P_k[core_map_new] - T_s[bank_map]
        T_th = np.full((A_tc.shape[0],), temp_max) - T_c[core_map_new] + A_lc@P_k[core_map_new] - T_s[core_map_new]

        #MaxTemp_bank = np.max(T_c[bank_map])
        #MaxTemp_core = np.max(T_c[core_map_new])
        #if (MaxTemp_bank > MaxTemp_core):
        #    #Situation_1 : temperature of Bank is the critical temperature.
        #    T_th = np.full((Ai.shape[0],), temp_max) - T_c[bank_map] + Ac@P_k[core_map_new] - T_s[bank_map]
        #if (MaxTemp_bank < MaxTemp_core):
        #    #Situation_2 : temperature of Core is the Critical temperature
        #    T_th = np.full((A_tc.shape[0],), temp_max) - T_c[core_map_new] + A_lc@P_k[core_map_new] - T_s[core_map_new]

    # Compute power budget with current active core mapping, solve power budget P
    P = np.linalg.solve(Ac, T_th) + P_s[core_map_new]
    # P = np.linalg.solve(Ac, T_th)
    print(P_k)
    print(T_c)

########################################################################################
########################################################################################
########################################################################################
########################################################################################

    #    ##################################
    #    ## Insert core GDP power , TP(total power) = memory power + core_GDP_power
    #    ##################################
    #    CoreMap = np.loadtxt('./system_sim_state/gdp_map.txt').astype(int)
    #    print(CoreMap)
    #    TP = P_k ;
    #    NewCoreMap = CoreMap + NUM ;
    #    Len = len(P)
    #    for j in range(0, Len):
    #        P_L = NewCoreMap[j].astype(int)
    #        TP[P_L] = P[j]
    #    TotalPower = TP

    #    NEW_P = P.copy() ## The new method core power
    #    ############################################	
    #    ## Optimization implement
    #    ############################################	
    #    length = len(CoreMap)
    #    for i in range(0,length):
    #        # print(i)
    #    #########################
    #    ## 1. get other temperautre influence matrix
    #    #########################
    #    # NUM = 16
    #        C_N = CoreMap[i].astype(int)
    #        mem_num = C_N.astype(int)
    #        core_num = (C_N + NUM).astype(int)  ## print(C_N)   print(core_num)

    #        ## other channel power
    #        P_other = TotalPower.copy()
    #        P_other[mem_num] = 0
    #        P_other[core_num] = 0 ## print(TP)     ## print(P_other)

    #        ## other channel matrix
    #        ## A_c : Core critical Power Matrix
    #        ## A_m : Mem  critical Power Matrix
    #        channel_map = np.zeros(A.shape[0] , )
    #        channel_map[C_N] = 1
    #        channel_map = np.asarray(channel_map, dtype = bool)
    #        A_o = np.atleast_2d(A[channel_map][:,:])
    #        T_rest = temp_max - T_c[channel_map] -  A_o@P_other - T_s[channel_map]

    #        ## critical channel matrix
    #        CoreNum = np.zeros(A.shape[0] ,)
    #        CoreNum[core_num]  = 1 ## print(CoreNum)
    #        CoreNum = np.asarray( CoreNum , dtype = bool)
    #        A_c = np.atleast_2d(A[channel_map][:,CoreNum])
    #        MemNum = np.zeros(A.shape[0] , )
    #        MemNum[mem_num]  = 1   ## print(MemNum)
    #        MemNum = np.asarray( MemNum , dtype = bool)
    #        A_m = np.atleast_2d(A[channel_map][:,MemNum])
    #        Ac = A_c[0][0]
    #        Am = A_m[0][0]
    #        pc = TotalPower[core_num]
    #        pm = TotalPower[mem_num]
    #        T_rest = T_rest + Ac * pc + Am * pm

    #        ###### constraint optimization
    #        e = 1e-10 # 非常接近0的值
    #        ##################################################
    #        ## 1.1 Aim 
    #        ##################################################
    #        ## fun = lambda x : 8 * (x[0] * x[1] * x[2]) # f(x,y,z) =8 *x*y*z
    #        fun = lambda x : (-1) / (0.62/x[0]  + ((x[0]/x[1])*0.0045))

    #        ##################################################
    #        ## 1.2 consPower
    #        ##################################################
    #        original_power = P_k[core_num]
    #        file_path = './PeriodicFrequency.log'
    #        with open(file_path, 'r') as file:
    #            lines = file.readlines()
    #            last_line = lines[-1].strip()  
    #        matrix = np.fromstring(last_line, sep=' ')  
    #        # original_freq = matrix[core_num].astype(float)
    #        original_freq = matrix[mem_num].astype(float)
    #        a = original_power / ( original_freq **3)
    #        b = 1.4     #  print(a)   # print(original_power)  # print(original_freq)
    #        Min_Freq = [1 , 0.1]  # below
    #        Max_Freq = [4 ,  1]  # above 
    #        bounds = [(Min_Freq[i], Max_Freq[i]) for i in range(len(Min_Freq))]

    #        ##################################################
    #        ## 1.3 Optimization 
    #        ##################################################
    #        cons = ({'type': 'eq', 'fun': lambda x: (a*x[0]**3)*Ac + ( b*x[1]*Am)  - T_rest})
    #        x0 = np.array((1.0, 1.0)) 
    #        res = minimize(fun, x0,bounds=bounds,method='SLSQP', constraints=cons)	
    #        #res.x[0] = res.x[0] + P_s[core_num]
    #        #res.x[0] = res.x[0] + P_s[core_num]
    #        print( res.x , res.fun)

    return P


