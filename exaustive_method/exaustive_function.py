# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 17:09:31 2024

@author: TANGI
"""

import calliope
import numpy as np
import time

#%% function which includes the storage and hydrogen technologies 

def calliope4exaustive(filekey, *dec_var):
    
    namefile_bridge = "bridgetxt_" + str(filekey) + ".txt"
       
    calliope.set_log_verbosity('error', include_solver_output=False)
       
    # Modify the data by modifying the energy_cap value in the model data
    ph = 'model_sulcis_exaustive.yaml'
    
    # define CALLIOPE model   
    model = calliope.Model(ph)
    
    #change objective weigth
    model.run_config['objective_options']['cost_class']['emissions']=dec_var[0]
    model.run_config['objective_options']['cost_class']['indipendence']=dec_var[1]
    model.run_config['objective_options']['cost_class']['PM_emissions']=dec_var[2]
    
    try:
        model.run()
        objs = model.get_formatted_array('cost').sum(['locs','techs']).to_pandas()  
        objs['monetary'] -= objs['revenues']
        objs = list(objs[['monetary', 'emissions', 'indipendence','PM_emissions']])
        
    except:
        objs = [np.power(10, 10), np.power(10, 10), np.power(10, 10), np.power(10, 10)]
    
    with open(namefile_bridge, "w") as f:
        for obj in objs:
            f.write(str(obj) + "\n") 
    
