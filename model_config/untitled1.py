# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 10:37:35 2023

@author: TANGI
"""

import calliope
import numpy as np
import time
import yaml
import os

#%%

def calliope4SP_baseline(filekey ,w_1,w_2,w_3):
    
    t_loop = time.time()
    
    namefile_bridge = "bridgetxt_" + str(filekey) + ".txt"
       
    calliope.set_log_verbosity('error', include_solver_output=False)
    
    tech_names = ['P2H','P2Heat_planned','battery','chp_hydrogen','hydrogen_storage','pv_planned_ground','pv_planned_roof','supply_heat_gpl','supply_heat_oil','supply_heat_solid','wind_planned_offshore','wind_planned_onshore']
       
    #change maximum capacity...

    ph = 'model_sulcis_SP.yaml'
        
    # define CALLIOPE model   
    model = calliope.Model(ph)
    
    #change objective weights
    model.run_config['objective_options']['cost_class']['emissions']=w_1
    model.run_config['objective_options']['cost_class']['indipendence']=w_2
    model.run_config['objective_options']['cost_class']['PM_emissions']=w_3
    
    # change maximum capacity by changing the model configuration directly
    # tech_data = model.inputs.loc_techs.data
    # idx = int(np.where(tech_data == ['X1::'+tech_names[tc]] )[0])   
    # if tc !=-1 :
    #     model.inputs.energy_cap_max.data[tc] = model.inputs.energy_cap_max.data[idx] + fixed_increase
    #     model.inputs.energy_cap_max.values[tc] = model.inputs.energy_cap_max.values[idx] + fixed_increase    
        
    try:
        model.run()
        objs = model.get_formatted_array('cost').sum(['locs','techs']).to_pandas()    
        objs = list(objs[['monetary', 'emissions', 'indipendence', 'PM_emissions','revenues','area','jobs']])
    
    except:
        objs = [np.power(10, 10), np.power(10, 10), np.power(10, 10), np.power(10, 10),np.power(10, 10),np.power(10, 10),np.power(10, 10)]
    
    with open("log_" + namefile_bridge, "w") as f:
        elapsed = time.time() - t_loop
        f.write( str(filekey) + " - " + time.strftime('%H:%M:%S', time.gmtime(elapsed)) + " - " + str(objs)  )
    
    with open(namefile_bridge, "w") as f:
        for obj in objs:
            f.write(str(obj) + "\n")


#%%

def calliope4SP(filekey ,fixed_increase, w_1,w_2,w_3, tc):
    
    tc = int(tc)
    t_loop = time.time()
    
    namefile_bridge = "bridgetxt_" + str(filekey) + ".txt"
       
    calliope.set_log_verbosity('error', include_solver_output=False)
    
    tech_names = ['P2H','P2Heat_planned','battery','chp_hydrogen','hydrogen_storage','pv_planned_ground','pv_planned_roof','supply_heat_gpl','supply_heat_oil','supply_heat_solid','wind_planned_offshore','wind_planned_onshore']
       
    #change maximum capacity...
    if tc !=-1 :
        # ...by changing the  .yaml file file
        with open('model_config_SP' + os.sep + 'techs_sulcis_SP.yaml', 'r') as file:
            techyaml = yaml.safe_load(file)

        with open('model_sulcis_SP.yaml', 'r') as file:
            modelyaml = yaml.safe_load(file)
            
        # Modify the data
        # Example: Changing a value in the YAML data
        techyaml['techs'][tech_names[tc] ]['constraints']['energy_cap_max'] += fixed_increase
        modelyaml['import'][0] =  'model_config_SP/techs_sulcis_' +  str(filekey) + '.yaml'
        
        # Save the modified data to a new file
        with open('model_config_SP' + os.sep + 'techs_sulcis_' +  str(filekey) + '.yaml', 'w') as file:
            yaml.dump(techyaml, file)
            
        with open('model_sulcis_' +  str(filekey) + '.yaml', 'w') as file:
            yaml.dump(modelyaml, file)
            
        ph = 'model_sulcis_' +  str(filekey) + '.yaml'
        
    else:
        ph = 'model_sulcis_SP.yaml'
        
    # define CALLIOPE model   
    model = calliope.Model(ph)
    
    #remove temporary .yaml file
    if tc !=-1 :
        os.remove('model_config_SP' + os.sep + 'techs_sulcis_' +  str(filekey) + '.yaml')
        os.remove(ph)
    
    #change objective weights
    model.run_config['objective_options']['cost_class']['emissions']=w_1
    model.run_config['objective_options']['cost_class']['indipendence']=w_2
    model.run_config['objective_options']['cost_class']['PM_emissions']=w_3
    
    # change maximum capacity by changing the model configuration directly
    # tech_data = model.inputs.loc_techs.data
    # idx = int(np.where(tech_data == ['X1::'+tech_names[tc]] )[0])   
    # if tc !=-1 :
    #     model.inputs.energy_cap_max.data[tc] = model.inputs.energy_cap_max.data[idx] + fixed_increase
    #     model.inputs.energy_cap_max.values[tc] = model.inputs.energy_cap_max.values[idx] + fixed_increase    
        
    try:
        model.run()
        objs = model.get_formatted_array('cost').sum(['locs','techs']).to_pandas()    
        objs = list(objs[['monetary', 'emissions', 'indipendence', 'PM_emissions','revenues','area','jobs']])
    
    except:
        objs = [np.power(10, 10), np.power(10, 10), np.power(10, 10), np.power(10, 10),np.power(10, 10),np.power(10, 10),np.power(10, 10)]
    
    with open("log_" + namefile_bridge, "w") as f:
        elapsed = time.time() - t_loop
        f.write( str(filekey) + " - " + time.strftime('%H:%M:%S', time.gmtime(elapsed)) + " - " + str(objs)  )
    
    with open(namefile_bridge, "w") as f:
        for obj in objs:
            f.write(str(obj) + "\n")
