# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 16:10:35 2023

@author: TANGI

"""

from platypus import *
import numpy as np
import os
import datetime
import pandas as pd
import random
import itertools
import shutil
import csv
import time
import re

#%% global parameters 
#define paraeters for simulation
n_dec_vars = 3  # Number of decision variables
n_objs = 4  # Number of objectives
n_seed = 1
nfe = 1000

#%% define functions

# Classe per la definizione del problema
class optimize_calliope(Problem):
    
    def __init__(self):
    
        super().__init__(n_dec_vars, n_objs)
        
        decision_var_range = [Real(0, 3), Real(0,30), Real(0,3)]

        self.types[:] = decision_var_range


    def evaluate(self, solution):
        
        t_loop = time.time()
        
        #create an unique identifier for the simulation
        filekey = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f") + str(round(random.random()*1000))
        varsstr = filekey
        
        name_script = "python -c \"from SA_function import *; calliope4SA(" + varsstr + ")\""
        
        # Chiamo script python che esegue il modello
        os.system(name_script)

        #read temporary files
        namefile_bridge = "bridgetxt_" + filekey + ".txt"
        
        # read objectives solution
        try:
            #load data
            objs = list(pd.read_csv(namefile_bridge, header=None).iloc[:, 0].values)
            cap = list(pd.read_csv("cap_"+namefile_bridge, header=None).iloc[:, 0].values)
            cp = list(pd.read_csv("cp_"+namefile_bridge, header=None).iloc[:, 0].values)
            
            #load file path
            result_path = pd.read_csv("output_file_name.txt", header=None).iloc[:, 0][0]
            with open(result_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(objs + [1] + cap + cp + [time.strftime('%H:%M:%S', time.gmtime(time.time() - t_loop))])
            
            os.remove(namefile_bridge)
            os.remove("cap_"+namefile_bridge)
            os.remove("cp_"+namefile_bridge)
                
        #exception if I don't find the file               
        except:

            #remove remaining files in folder
            pattern = re.compile(filekey)
            for filename in os.listdir():
                 if filename.endswith('.txt'):
                     if re.search(pattern, filename):
                         os.remove(filename)        
           
        # Aggiorno soluzione
        solution.objectives[:] = np.array(objs)
    
def optimize_scenario(id_sim,result_folder):
    
    # define the problem 
    problem = optimize_calliope()
    
    starttime = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    
    # Where to save seed and runtime files
    os_fold = os.sep  # Folder operator for operating system
    output_location = result_folder + os.sep  + r'scenario_' +str(id_sim) # Specify location of output files for different seeds
    
    if not os.path.exists(output_location):
        # if the folder directory is not present 
        # then create it.
        os.makedirs(output_location)
            
    #create txt with log and results
    namelog =  output_location + os_fold + "check" + starttime +'.txt'
    
    #create csv file for other results
    column_names = ['monetary', 'emissions', 'indipendence', 'PM_emissions', 'monetary.w',
           'emissions.w', 'indipendence.w', 'PM_emissions.w', 'pv_planned_ground',
           'pv_planned_roof', 'wind_planned_onshore', 'wind_planned_offshore',
           'P2Heat_planned', 'supply_heat_solid', 'supply_heat_oil',
           'supply_heat_gpl', 'battery', 'supply_grid_power.p', 'pv_existing.p',
           'pv_planned_ground.p', 'pv_planned_roof.p', 'wind_existing.p',
           'wind_planned_onshore.p', 'wind_planned_offshore.p', 'P2Heat_existing.p',
           'P2Heat_planned.p', 'supply_heat_solid.p', 'supply_heat_oil.p',
           'supply_heat_gpl.p', 'battery.p', 'runtime']

    # run for each seed
    for s in range(0,n_seed):
        
        with open(namelog, "a") as f:
            f.write('Seed '+ str(s) +'\n')    
    
        # Write data to the CSV file
        # Define the CSV file name
        file_name = output_location + os_fold + "savedata_" + str(id_sim) + "_"+ str(s) +'.csv'
        
        with open("output_file_name.txt", "w") as f:
            f.write(file_name) 
                
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(column_names)
            
        #create log text
        filetxt = open(namelog, "w")
        filetxt.writelines(['CALLIOPE with OMOPSO with weigths - log of all sim - : ', datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n \n'])
        filetxt.close()
    
        # initiate the optimization algorithm to run in parallel
        with ProcessPoolEvaluator(24) as evaluator:
            algorithm = OMOPSO(problem, evaluator=evaluator, epsilons =  [2090103,3497889,602844,5004418])
            algorithm.run(nfe)
            
        nondominated_solutions=nondominated(algorithm.result)
        obj = np.ndarray(shape = (len(nondominated_solutions), n_objs)) # obiettivo
        theta = np.ndarray(shape = (len(nondominated_solutions), n_dec_vars)) # parametri
    
        i = 0
        for solution in nondominated_solutions:
            obj[i, :] = solution.objectives[:]
            theta[i, :] = solution.variables[:]
            i  = i + 1
            
        # save results in txt
        nameobj =  output_location + os_fold + "obj_" + str(id_sim) + "_"+ str(s) +'.txt'
        nametheta =  output_location + os_fold + "theta_" + str(id_sim) + "_"+ str(s) +'.txt'
    
        np.savetxt(nameobj, obj, fmt="%.18e", delimiter=" ")
        np.savetxt(nametheta, theta, fmt="%.18e", delimiter=" ")
    
        with open(namelog, "a") as f:
            f.write('\n end seed: '+ str(s) + ' - ' +  datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '\n' )    
    
if __name__ == "__main__":
    
    # Three example lists with three elements each
    PUN = ['PUN_avg_2015', 'PUN_max_2008','PUN_min_2016']
    PV = ['PV_energy_production_avg_2015', 'PV_energy_production_max_2017','PV_energy_production_min_2018']
    WS = ['Wind_energy_production_avg_2015', 'Wind_energy_production_max_2019','Wind_energy_production_min_2008']
    
    os_fold = os.sep  # Folder operator for operating system
   
    # Generate all combinations using itertools.product
    combinations = list(itertools.product(PUN, PV, WS))
    
    #define folder with results
    result_folder = 'sets_SA_' + datetime.datetime.now().strftime("%Y%m%d_%H%M")
    if not os.path.exists(result_folder):
        # if the folder directory is not present 
        # then create it.
        os.makedirs(result_folder)
            
    # Define source and destination folders
    source_folder = 'timeseries_data_SA'
    destination_folder = 'timeseries_data_active'
    
    # run for each combination
    for c in range(0,len(combinations)):
    
        #Copy and rename new files from the source folder to the destination folder
        for filename in combinations[c]:
            
            filename_csv = filename +'.csv'
            source_file_path = os.path.join(source_folder, filename_csv)
            
            if os.path.isfile(source_file_path):
                # You can define a new name for the file as per your requirements
                
                if filename_csv[0:2]=='Wi': new_filename = 'wind_resource.csv'
                if filename_csv[0:2]=='PU': new_filename = 'PUN.csv'
                if filename_csv[0:2]=='PV': new_filename = 'pv_resource.csv'
                
                destination_file_path = os.path.join(destination_folder, new_filename)
                shutil.copy(source_file_path, destination_file_path)
                
        optimize_scenario(c,result_folder)
