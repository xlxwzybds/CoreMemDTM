import shutil
import numpy as np
import time

NOF_CORE_SETTINGS = 2
NOF_CORE = 16
NOF_CHANNELS = 8
#CORE_DTM_THRESHOLD_LP = 78.0


MEM_ACTIVE = 0
MEM_LOW_POWER = 1

CORE_ACTIVE = 0             #HF
CORE_F1 = 1                 #HF
CORE_F2 = 2                 #MF
CORE_F3 = 3                 #LF
CORE_LOW_POWER = 4



max_temperature_core = 0
k_DVFS = 1  # Epoch - 1
last_core = 0
N_RR_Core = 0

Freq_Downgrade = np.zeros(NOF_CORE)

max_temperature_Mem = 0
last_Mem = 0
N_RR_Mem = 0

thermal_limit_core = 80 # for bodttrack , swaptions , blackscholes , radiosity
#thermal_limit_core = 71 # for bodttrack , swaptions , blackscholes
#thermal_limit_core = 74 # for streamcluster
thermal_limit_Mem = 80 
#thermal_limit_Mem = 78  # for bodytrack
CORE_DTM_THRESHOLD  = (thermal_limit_core -4 )    # Important , it will used in main function
MEM_DTM_THRESHOLD   = (thermal_limit_Mem - 4)     # Important , main function
#thermal_limit_core = 77
#thermal_limit_Mem = 80 
#CORE_DTM_THRESHOLD  = (thermal_limit_core -7 )    # Important , it will used in main function
#MEM_DTM_THRESHOLD   = (thermal_limit_Mem - 4)     # Important , main function
#

COMPUTE = 0
MIXED = 1
MEMORY = 2
# 0 - compute
# 1 - mixed
# 2 - memory
# Intial value benchmark_type array. Dyanmically computed each epoch.


def dtm_mem(timestep ,memory_temperature_trace, ):
    global memory_state

    ## NOF_CHANNELS is bank_num/channel_num. 
    ## There NOF_CHANNELS is 16
    sort_index = np.argsort(memory_temperature_trace)
    rev_sort_index = sort_index[::-1]
    max_temperature_Mem = np.max(memory_temperature_trace)
    # print ("rev_sort_index, " , rev_sort_index)

    #print ("Mem Round Robin")
    #print ("max_temperature_Mem," , '%.2f'%max_temperature_Mem)
    ### for blackscholes , swaptions  ,radiosity
    if (max_temperature_Mem >= thermal_limit_Mem):
        #N_RR_Mem = 9  for bodytrack and swaption
        N_RR_Mem = 4
    elif (max_temperature_Mem >= (thermal_limit_Mem -0.5)):
        N_RR_Mem = 3
    elif (max_temperature_Mem >= (thermal_limit_Mem -1.0)):
        N_RR_Mem = 2
    elif (max_temperature_Mem >= (thermal_limit_Mem -1.5)):
        N_RR_Mem = 1
    elif (max_temperature_Mem >= (thermal_limit_Mem -2.0)):
        N_RR_Mem = 0 
    elif (max_temperature_Mem >= (thermal_limit_Mem -2.5)):
        N_RR_Mem = 0 
    elif (max_temperature_Mem >= (thermal_limit_Mem -3.0)):
        N_RR_Mem = 0
    elif (max_temperature_Mem >= (thermal_limit_Mem -3.5)):
        N_RR_Mem = 0
    elif (max_temperature_Mem >= (thermal_limit_Mem -4.0)):
        N_RR_Mem = 0
    else:
        N_RR_Mem = 0

    global last_Mem

        # print ("Mem RR List", end = ', ')
    # Make all active
    x = 0
    while x < NOF_CHANNELS:
        memory_state[x] = MEM_ACTIVE
        x = x + 1


    #print ("\nNew Mem RR List", end = ', ')
    x = 0
    while x < N_RR_Mem:
        # print(i,end ='')
        i = rev_sort_index[x]
        #print(i, end = ', ')
        memory_state[i] = MEM_LOW_POWER
        x = x + 1
    #print ("")
    #print( memory_state);
    # return "two Done"





#def dtm_core(timestep , core_temperature_trace , core_temperature_trace_K , memory_temperature_trace):
def dtm_core(timestep ,core_temperature_trace , core_temperature_trace4, core_temperature_trace3, core_temperature_trace2, core_temperature_trace1):
    
    ## Long epoch interval average core temperature
    ## K-epoch interval average core temperature
    global long_term_avg_core_temperature
    global avg_k_core_temperature
    global core_freq
    global core_freq_rr
    global core_state
    global memory_state

    # Get the current core temperature
    # avg_temperature_core = np.average(core_temperature_trace[timestep])
    avg_temperature_core = np.average(core_temperature_trace)

    # Need a file to keep the value of timestep
    # Need know k_DVFS values
    #       timestep % k_DVFS = 0 => Time for DVFS
    if (not(timestep % k_DVFS)):
        # print ("Core DVFS")

        ## For the first time
        if not(timestep):
            # print ("First time")
            # long_term_avg_core_temperature = core_temperature_trace[0]
            #
            # Generate List , the length of list is NOF_CORE
            avg_k_core_temperature = np.zeros(NOF_CORE)
            max_k_core_temperature = np.zeros(NOF_CORE)
        else:

            # core_temperature_trace_sum_k = core_temperature_trace[timestep-(k_DVFS-1)]
            # max_k_core_temperature = core_temperature_trace[timestep-(k_DVFS-1)]
            core_temperature_trace_sum_k = core_temperature_trace
            max_k_core_temperature       = core_temperature_trace
            # print (timestep-(k_DVFS-1))
            # print (core_temperature_trace_sum_k)

            # for x in range(1, k_DVFS-1):
            for x in range(1, k_DVFS-1):
                #print (x)
                # print (timestep - x)
                # print (core_temperature_trace[timestep - x])
                core_temperature_trace_sum_k = core_temperature_trace_sum_k + core_temperature_trace
                max_k_core_temperature = np.maximum(max_k_core_temperature, core_temperature_trace)

            avg_k_core_temperature = core_temperature_trace_sum_k 
            max_k_core_temperature = max_k_core_temperature

            #avg_k_core_temperature = (core_temperature_trace_sum_k + core_temperature_trace4 + core_temperature_trace3 + core_temperature_trace2 + core_temperature_trace1 )/k_DVFS
            #max_k_core_temperature = np.maximum(max_k_core_temperature, core_temperature_trace4 )
            #max_k_core_temperature = np.maximum(max_k_core_temperature, core_temperature_trace3 )
            #max_k_core_temperature = np.maximum(max_k_core_temperature, core_temperature_trace2 )
            #max_k_core_temperature = np.maximum(max_k_core_temperature, core_temperature_trace1 )

        #print ("max_k_core_temperature, " , max_k_core_temperature)

        
        ## Gernerate the zero numpy
        Heated_Core = np.zeros(NOF_CORE)
        core_freq = np.zeros(NOF_CORE)
        core_freq_rr = np.zeros(NOF_CORE)



        for x in range(NOF_CORE):
            Heated_Core[x] = 1
            #######################################
            ### for swaptions and blacksholes , for core-3,core-7 , radiosity
            #######################################
            #if (max_k_core_temperature[x] >= thermal_limit_core):
            #    Freq_Downgrade[x] = 4
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 0.5)): ## 79.5
            #    Freq_Downgrade[x] = 3
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 1.0)): ## 79
            #    Freq_Downgrade[x] = 2 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 2)): ## 78
            #    Freq_Downgrade[x] = 1
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 2.5)): ## 77.7
            #    Freq_Downgrade[x] = 1 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 3)): ## 77
            #    Freq_Downgrade[x] = 1 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 3.5)): # 73.5
            #    Freq_Downgrade[x] = 1 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 4)): 
            #    Freq_Downgrade[x] = 1 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 6)): ##
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 8)): ##
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 10)): #
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 12)): #
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 15)): #
            #    Freq_Downgrade[x] = 0
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 20)): #
            #    Freq_Downgrade[x] = 0
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 25)):
            #    Freq_Downgrade[x] = 0
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 30)):
            #    Freq_Downgrade[x] = 0
            #else:
            #    #if not(benchmark_type[x] == 2):
            #    #   Freq_Downgrade[x] = 0
            #    #   Heated_Core[x] = 0
            #    Freq_Downgrade[x] = 2
            #    Heated_Core[x] = 0
            #######################################
            ### for swaptions and blacksholes , for core-12
            #######################################
            #if (max_k_core_temperature[x] >= thermal_limit_core):
            #    Freq_Downgrade[x] = 4
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 0.5)): ## 79.5
            #    Freq_Downgrade[x] = 3
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 1.0)): ## 79
            #    Freq_Downgrade[x] = 3 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 2)): ## 78
            #    Freq_Downgrade[x] = 3
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 2.5)): ## 77.7
            #    Freq_Downgrade[x] = 2 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 3)): ## 77
            #    Freq_Downgrade[x] = 2 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 3.5)): # 73.5
            #    Freq_Downgrade[x] = 1 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 4)): 
            #    Freq_Downgrade[x] = 1 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 6)): ##
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 8)): ##
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 10)): #
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 12)): #
            #    Freq_Downgrade[x] = 0 
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 15)): #
            #    Freq_Downgrade[x] = 0
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 20)): #
            #    Freq_Downgrade[x] = 0
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 25)):
            #    Freq_Downgrade[x] = 0
            #elif (max_k_core_temperature[x] >= (thermal_limit_core - 30)):
            #    Freq_Downgrade[x] = 0
            #else:
            #    #if not(benchmark_type[x] == 2):
            #    #   Freq_Downgrade[x] = 0
            #    #   Heated_Core[x] = 0
            #    Freq_Downgrade[x] = 2
            #    Heated_Core[x] = 0
            ########################################
            ### for bodytrack & streamcluster
            #######################################
            if (max_k_core_temperature[x] >= thermal_limit_core):
                Freq_Downgrade[x] = 4
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 0.5)): ## 76.5
                Freq_Downgrade[x] = 3
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 1.0)): ## 76
                Freq_Downgrade[x] = 3
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 1.5)): ## 75
                Freq_Downgrade[x] = 3
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 2.0)): ## 75
                Freq_Downgrade[x] = 3
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 2.5)): ## 74.5
                Freq_Downgrade[x] = 2
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 3)): ## 74
                Freq_Downgrade[x] = 2
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 3.5)): # 73.5
                Freq_Downgrade[x] = 1
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 4)): 
                Freq_Downgrade[x] = 1
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 6)): ##
                Freq_Downgrade[x] = 0
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 8)): ##
                Freq_Downgrade[x] = 0
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 10)): #
                Freq_Downgrade[x] = 0
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 12)): #
                Freq_Downgrade[x] = 0 
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 15)): #
                Freq_Downgrade[x] = 0
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 20)): #
                Freq_Downgrade[x] = 0
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 25)):
                Freq_Downgrade[x] = 0
            elif (max_k_core_temperature[x] >= (thermal_limit_core - 30)):
                Freq_Downgrade[x] = 0
            else:
                #if not(benchmark_type[x] == 2):
                #   Freq_Downgrade[x] = 0
                #   Heated_Core[x] = 0
                Freq_Downgrade[x] = 2
                Heated_Core[x] = 0

        x = 0
        while x < NOF_CORE:
            core_freq[x] = Freq_Downgrade[x]
            x = x + 1

        #print ("Freq_Downgrade, " , Freq_Downgrade)


    # print ("Core Round Robin")
    # print ("max_temperature_core, " , '%.2f'%max_temperature_core)
    if (max_temperature_core >= thermal_limit_core):
        N_RR_Core = 10
    elif (max_temperature_core >= (thermal_limit_core -3)):
        N_RR_Core = 8
    elif (max_temperature_core >= (thermal_limit_core -5)):
        N_RR_Core = 8
    elif (max_temperature_core >= (thermal_limit_core -10)):
        N_RR_Core = 6
    elif (max_temperature_core >= (thermal_limit_core -15)):
        N_RR_Core = 6
    elif (max_temperature_core >= (thermal_limit_core -20)):
        N_RR_Core = 6
    elif (max_temperature_core >= (thermal_limit_core -22)):
        N_RR_Core = 5
    elif (max_temperature_core >= (thermal_limit_core -25)):
        N_RR_Core = 4
    elif (max_temperature_core >= (thermal_limit_core -28)):
        N_RR_Core = 4
    elif (max_temperature_core >= (thermal_limit_core -30)):
        N_RR_Core = 3
    else:
        N_RR_Core = 3

    global last_core


    ## Initial_time , make all core High frequency
    if (timestep == 0):
        # Make all active
        x = 0
        while x < NOF_CORE:
            core_freq[x] = 0                # High Freq
            core_freq_rr[x] = 0             # High Freq
            x = x + 1
    else:
        # Intializing core_freq_rr at each invocation
        x = 0
        while x < NOF_CORE:
            core_freq_rr[x] = core_freq[x]
            x = x + 1


    if (avg_temperature_core < (max_temperature_core - 1.0)):
        if (N_RR_Core > 0):
            #print ("Update")
            N_RR_Core = N_RR_Core - 1


    print ("Core RR List", end = ', ')
    # Round-Robin Freq. reduction
    i = last_core
    x = 0
    while x < N_RR_Core:
        # print(i,end ='')
        # print(i, end = ', ')
        #core_freq_rr[i] = core_freq_rr[i] + 1   # Downgrade by 1
        core_freq_rr[i] = core_freq_rr[i] + 1   # Downgrade by 1
        i = (i+1)%NOF_CORE
        x = x + 1

    last_core = i


    # Frequency to state-mapping
    # CORE_LOW_POWER could also be used later
    x = 0
    while x < NOF_CORE:

        if (core_freq_rr[x] == 0):
            core_state[x] = CORE_ACTIVE
        elif (core_freq_rr[x] == 1):
            core_state[x] = CORE_F1
        elif (core_freq_rr[x] == 2):
            core_state[x] = CORE_F2
        elif (core_freq_rr[x] == 3):
            core_state[x] = CORE_F3
        elif (core_freq_rr[x] == 4):
            core_state[x] =CORE_F3
        else:
            core_state[x] = CORE_F3
        x = x + 1
    #print ("")
    # return "one Done"


def none(timestep):
    for x in range(NOF_CORE):
            Freq_Downgrade[x] = 0   # High Freq
            core_state[x] = CORE_ACTIVE
    print ("Freq_Downgrade," , Freq_Downgrade)


#switcher = {
#        0: none,
#        1: dtm_core,
#        2: dtm_mem,
#        3: both
#    }
#

def dtm(argument,timestep):
    # Get the function from switcher dictionary
    func = switcher.get(argument, "nothing")
    # Execute the function
    return func(timestep)


core_freq = np.zeros(NOF_CORE)
core_freq_rr = np.zeros(NOF_CORE)
core_state = np.zeros(NOF_CORE ) 
memory_state =np.zeros(NOF_CORE)

def main():
    #start_time = time.time()
    #end_time = time.time()
    #execution_time = end_time - start_time
    #print(f"core execution time: {execution_time:.9f} ")

    ###############################
    ## 1. read FILE
    ###############################
    global core_state
    global memory_state
    
    core_state_file = './CoreMemDTM/core_state.txt'
    time_step = np.loadtxt('./CoreMemDTM/timestep.trace')
    all_temperature_trace = np.loadtxt('./combined_insttemperature.trace',skiprows=1)
    all_temperature_trace4 =np.loadtxt( "./CoreMemDTM/combined_insttemperature4.trace",skiprows=1) 
    all_temperature_trace3 =np.loadtxt( "./CoreMemDTM/combined_insttemperature3.trace",skiprows=1)
    all_temperature_trace2 =np.loadtxt( "./CoreMemDTM/combined_insttemperature2.trace",skiprows=1)
    all_temperature_trace1 =np.loadtxt( "./CoreMemDTM/combined_insttemperature1.trace",skiprows=1)
    print("all_temperature_trace is ", all_temperature_trace)

    start_time = time.time()
    core_temperature_trace  = all_temperature_trace[:NOF_CORE]
    core_temperature_trace4 = all_temperature_trace4[:NOF_CORE]
    core_temperature_trace3 = all_temperature_trace3[:NOF_CORE]
    core_temperature_trace2 = all_temperature_trace2[:NOF_CORE]
    core_temperature_trace1 = all_temperature_trace1[:NOF_CORE]
    memory_temperature_trace = all_temperature_trace[NOF_CORE:]
    new_step = time_step

    ###############################
    ## 2. Core DTM
    ###############################
    max_temperature_core = np.max(core_temperature_trace)
    max_temperature_Mem = np.max(memory_temperature_trace)
    # Four Situations , and four Method to solve
    dtm_core(new_step ,core_temperature_trace , \
            core_temperature_trace4 ,\
            core_temperature_trace3 ,\
            core_temperature_trace2 ,\
            core_temperature_trace1 )
    #else:
    #    none(new_step)
    if (max_temperature_Mem >= MEM_DTM_THRESHOLD):
        dtm_mem(new_step ,memory_temperature_trace )

    for i in range(0, NOF_CORE):
        if (memory_state[i] == MEM_LOW_POWER):
            core_state[i] = CORE_LOW_POWER
            #continue
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"core execution time: {execution_time:.9f} ")
    print('core state is , ',core_state)

    source_file_5 = "./combined_insttemperature.trace"
    source_file_4 = "./CoreMemDTM/combined_insttemperature4.trace"
    source_file_3 = "./CoreMemDTM/combined_insttemperature3.trace"
    source_file_2 = "./CoreMemDTM/combined_insttemperature2.trace"
    source_file_1 = "./CoreMemDTM/combined_insttemperature1.trace"
    # Notice the turn , 2-1  , 3-2 , 4-3, 5-4
    shutil.copyfile(source_file_2, source_file_1)
    shutil.copyfile(source_file_3, source_file_2)
    shutil.copyfile(source_file_4, source_file_3)
    shutil.copyfile(source_file_5, source_file_4)

    new_step += 1
    new_step = new_step.item()

    with open('./CoreMemDTM/timestep.trace', 'w') as step_file:
        step_file.write(str(new_step))

    with open(core_state_file, 'w') as core_file:
        core_file.write(" ".join(map(str, core_state)))



if __name__ == "__main__" :
    main()    
