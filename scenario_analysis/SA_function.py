# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 16:10:35 2023

@author: TANGI

This calliope function is created to be coupled with a multiobjective evolutionary algorithm (MOEA) with decision variables equal 
to the weigth for each objective used in CALLIOPE
"""

import calliope
import numpy as np

#%% function which includes the storage and hydrogen technologies 

def calliope4SA(filekey, *dec_var):
    
    namefile_bridge = "bridgetxt_" + str(filekey) + ".txt"
       
    calliope.set_log_verbosity('error', include_solver_output=False)
       
    # Modify the data by modifying the energy_cap value in the model data
    ph = 'model_sulcis_SA.yaml'
    
    # define CALLIOPE model   
    model = calliope.Model(ph)

    #extract names
    name_tech = ['pv_planned_ground', 'pv_planned_roof', 'wind_planned_onshore', 'wind_planned_offshore',
                      'P2Heat_planned', 'supply_heat_solid' , 'supply_heat_oil', 'supply_heat_gpl', 'battery']
    name_tech_prod = ['supply_grid_power','pv_existing','pv_planned_ground', 'pv_planned_roof','wind_existing', 'wind_planned_onshore',
                    'wind_planned_offshore','P2Heat_existing', 'P2Heat_planned', 'supply_heat_solid' , 'supply_heat_oil', 'supply_heat_gpl','battery']
   
    #change objective weigth
    model.run_config['objective_options']['cost_class']['emissions']=dec_var[0]
    model.run_config['objective_options']['cost_class']['indipendence']=dec_var[1]
    model.run_config['objective_options']['cost_class']['PM_emissions']=dec_var[2]
    
    try:
        model.run()
        objs = model.get_formatted_array('cost').sum(['locs','techs']).to_pandas()
        objs['monetary'] -= objs['revenues']
        
        # demand_tot = model.get_formatted_array('resource').sum(['locs']).to_pandas().T[['demand_electricity','demand_heat' ]].sum().sum()
        # energy_grid_prod = model.get_formatted_array('carrier_prod').sum(['locs','carriers','timesteps']).to_pandas().T[['supply_grid_power']]
        # objs['indipendence'] = energy_grid_prod/-demand_tot
        
        objs = list(objs[['monetary', 'emissions', 'indipendence','PM_emissions']])
        
        #save also energy cap and storage cap
        energy_cap = list(model.get_formatted_array('energy_cap').sum(['locs']).to_pandas()[name_tech].T)
        storage_cap = list(model.get_formatted_array('storage_cap').sum(['locs']).to_pandas().T)
        energy_cap[-1] = storage_cap[0]
        
        # find which carrier is used in the system
        car = model.get_formatted_array('carrier_prod')['carriers'].to_pandas().T
        cp_el = model.get_formatted_array('carrier_prod').loc[{'carriers':car[0]}].sum(['locs','timesteps']).to_pandas()[name_tech_prod] #production of each tech for carrier i
        cp_heat = model.get_formatted_array('carrier_prod').loc[{'carriers':car[1]}].sum(['locs','timesteps']).to_pandas()[name_tech_prod]#production of each tech for carrier i
        cp = list(cp_el + cp_heat )
        
    except:
        objs = [np.power(10, 10), np.power(10, 10), np.power(10, 10), np.power(10, 10)]
        energy_cap = 0
        cp = 0
    
    #Save temporary bridge files
    with open(namefile_bridge, "w") as f:
        for obj in objs:
            f.write(str(obj) + "\n") 
    
    with open("cap_" + namefile_bridge, "w") as f:
        if energy_cap is not int:
            for c in energy_cap:
                f.write(str(c) + "\n") 
        else:
             f.write("\n")        
            
    with open("cp_" + namefile_bridge, "w") as f:
        if cp is not int:
            for c in cp:
                f.write(str(c) + "\n") 
        else:
             f.write("\n") 