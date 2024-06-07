# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 17:05:53 2024

@author: TANGI
"""

import numpy as np
import time
import pandas as pd
import os 
from joblib import Parallel, delayed
from scipy.stats import qmc

#%% global variables

num_cores = 20

#extract sobol sequence
n_sim = 2**13
weight_range = np.array([[0, 3], [0,30], [0, 3]]).T

sampler = qmc.Sobol(d=3, scramble=False)
Sobolsample = (sampler.random(n_sim) * (weight_range[1,:] - weight_range[0,:]) +weight_range[0,:])
      
#create folder to contain results
starttime = time.strftime("%Y%m%d_%H%M", time.gmtime())
    
# Where to save seed and runtime files
output_location = r'result_exaustive' # Specify location of output files for different seeds
os_fold = os.sep  # Folder operator for operating system

# if the folder directory is not present 
# then create it.
if not os.path.exists(output_location):

    os.makedirs(output_location)
        
#create txt results
nameres =  output_location + os_fold + "results" +'.txt'

filetxt = open(nameres, "w")
filetxt.close()

namelog = output_location + os_fold + "log"  +'.txt'
filetxt = open(namelog, "w")
filetxt.close()

#%% define Calliope function

def calliope_borg_call(id_sim):

    t_loop = time.time()
    
    sim_par = Sobolsample[id_sim,:]
    
    idbridge = int(time.strftime("%Y%m%d%H%M", time.gmtime())) + id_sim
    
    varsstr = str(idbridge) + "," +  str(sim_par[0]) + "," +  str(sim_par[1])+ "," + str(sim_par[2])
    name_script = "python -c \"from exaustive_function import *; calliope4exaustive(" + varsstr + ")\""
    
    # Chiamo script python che esegue il modello
    os.system(name_script)
    
    namefile_bridge = "bridgetxt_" + str(idbridge) + ".txt"

    # read objectives soluzione
    objs = list(pd.read_csv(namefile_bridge, header=None).iloc[:, 0].values)
    os.remove(namefile_bridge)
        
    elapsed = time.time() - t_loop
    
    objs.insert(0,id_sim)
    with open(namelog, "a") as f:
        f.write(str(objs) + ' - ' + time.strftime('%H:%M:%S', time.gmtime(elapsed)) + ' - ' + time.strftime('%H:%M:%S', time.gmtime()) + "\n")
        
    with open(nameres, "a") as f:
        f.write(str(objs) + "\n")
        
#%% run parallel computation

Parallel(n_jobs=num_cores)(delayed(calliope_borg_call)(id_sim) for id_sim in range(0,Sobolsample.shape[0] ) )
    
#%% save data to dataframe

columns = ['monetary', 'emissions', 'indipendence', 'PM_emissions']

# Load the CSV file
with open(nameres, 'r') as file:
    # Read the file and remove all ']' characters
    cleaned_data = [line.replace(']', '').replace('[', '') for line in file]

split_data = [row.split(',') for row in cleaned_data]

# Create a DataFrame with the cleaned data and specified column names
df = pd.DataFrame(split_data)
df = df.astype(float)
df.index = df[0].astype(int)
df = df.drop(columns=[0])
df = df.sort_index().rename_axis('Index')
df.columns=columns

df.to_csv(nameres)

