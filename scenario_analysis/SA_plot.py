# -*- coding: utf-8 -*-
"""
Created on Wed Mar  6 10:42:16 2024

@author: TANGI
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import seaborn as sns

#%%

def average_values(obj_monetary,energy_cap_t, boundary_ranges):
    result_mean = np.zeros((len(boundary_ranges)))
    results_sum = np.zeros((len(boundary_ranges)))
    results_num = np.zeros((len(boundary_ranges)))

    for r in range(len(boundary_ranges)):
        # Extract indices of elements within the current range
        indices = np.where((obj_monetary >= boundary_ranges[r, 0]) & (obj_monetary <= boundary_ranges[r, 1]))[0]

        # Calculate the average of the corresponding elements in the second column
        if len(indices) > 0:
            result_mean[r] = np.mean(energy_cap_t[indices])
            results_sum[r] = np.sum(energy_cap_t[indices])
            results_num[r] = len(energy_cap_t[indices])
        else:
            result_mean[r] = np.nan
            
    return results_sum,results_num,result_mean

#%%

def extract_ranges_info(pathfold, obj_slice , boundary_ranges, namefile ):
    
    #create model for basic data

    import calliope
    
    #remove warnings
    calliope.set_log_verbosity('error', include_solver_output=False)
    
    #load model      
    path = 'model_sulcis_SA.yaml' #'model_sulcis_operation.yaml'
            
    model = calliope.Model(path)
    
    name_tech = ['pv_planned_ground', 'pv_planned_roof', 'wind_planned_onshore', 'wind_planned_offshore',
                      'P2Heat_planned', 'supply_heat_solid' , 'supply_heat_oil', 'supply_heat_gpl', 'battery']
    
    #define parameters   
    tech_el = ['pv_planned_ground', 'pv_planned_roof', 'wind_planned_onshore', 'wind_planned_offshore','battery']
    objs = ['monetary', 'emissions', 'indipendence','PM_emissions']           
    num_scenario = 9 * 3  
    
    #extract energy_cap_max for all tech
    energy_cap_max = model.get_formatted_array('energy_cap_max').sum(['locs']).to_pandas()[name_tech]
    energy_cap_max['battery'] = model.get_formatted_array('storage_cap_max').sum(['locs']).to_pandas()['battery']
    
    #total demand satisfied via the technology
    demand_sum = pd.DataFrame(np.zeros((len(boundary_ranges), len(name_tech))), columns=name_tech) 
    
    # Create an empty dictionary to store DataFrames
    # demand_mean_allsim contains the average demand satisfied for each tech in each range, for all the scenario considered
    demand_mean_allsim = {}
    
    #total number of non-dominated scenarios in each range
    data_num = np.zeros(len(boundary_ranges)) 
   
    #for each scenario
    for i in range(0,num_scenario):
        
        namefolder = 'scenario_' + str(i)
    
        os_fold = os.sep
        
        nondominated_data = pd.read_csv(pathfold + os_fold + namefolder + os_fold + 'nondominated'+namefile+'.csv')
        
        if obj_slice==1:
            obj_considered = np.array(nondominated_data[objs[obj_slice]].apply(lambda x: x/10**9)) #if CO2
        else:
            obj_considered = np.array(nondominated_data[objs[obj_slice]].apply(lambda x: x/10**6)) #if monetary
            
        #demand_mean contains the mean demand satisfied (in % to the total demand) for each tech in the scenario considered, for each economic range
        demand_mean = pd.DataFrame(np.zeros((len(boundary_ranges), len(name_tech))), columns=name_tech)
           
        column_names_prod = ['supply_grid_power.p', 'pv_existing.p',
               'pv_planned_ground.p', 'pv_planned_roof.p', 'wind_existing.p',
               'wind_planned_onshore.p', 'wind_planned_offshore.p', 'battery.p', 
               'P2Heat_existing.p','P2Heat_planned.p', 'supply_heat_oil.p', 'supply_heat_gpl.p', 'supply_heat_solid.p']

        energy_vector = [0,0,0,0,0,0,0,0,1,1,1,1,1] #0=el, 1=heat
        production_results = nondominated_data[column_names_prod]
        
        a=production_results*[1 if value == 0 else 0 for value in energy_vector]
        prod_electricity = a.sum(axis=1)
        
        a=production_results* energy_vector
        prod_heat = a.sum(axis=1)

        #run for each tech
        for t in range(0,len(name_tech)):
            
            #for each scenario, find how much demand the tech is satisfying
            if name_tech[t] in tech_el:
                demand_satisfied_t = np.array(nondominated_data[name_tech[t]+'.p']/prod_electricity)
            else:
                demand_satisfied_t = np.array(nondominated_data[name_tech[t]+'.p']/prod_heat)
                    
            results_dem_sum, results_num, result_dem_mean = average_values(obj_considered, demand_satisfied_t, boundary_ranges)
            
            demand_sum[name_tech[t]] = np.array(demand_sum[name_tech[t]]) + results_dem_sum
            demand_mean[name_tech[t]] = np.array(result_dem_mean)
                
         # Create DataFrame and add it to the dictionary with a key
        dataframe_key = f'scenario_{i}'
        demand_mean_allsim[dataframe_key] = demand_mean
        
        data_num = np.array(data_num).T + results_num
           
    #demand_mean_tot contains the energy_cap installed for each tech for each economic range, averaged across all scenarios
    demand_mean_tot = demand_sum.div(data_num, axis=0)
    
    return demand_mean_tot, demand_mean_allsim

#%%

#path to data
pathfold = 'results_SA_allseed'

# namefile = '_' + str(i) + '_0'
namefile = '_pareto'

name_tech = ['pv_planned_ground', 'pv_planned_roof', 'wind_planned_onshore', 'wind_planned_offshore',
                  'P2Heat_planned', 'supply_heat_solid' , 'supply_heat_oil', 'supply_heat_gpl', 'battery']
objs = ['monetary', 'emissions', 'indipendence','PM_emissions']    
num_scenario = 9 * 3  

#ranges for monetary
ranges = range(40,150,10)
boundary_ranges = np.vstack((ranges[0:-1],ranges[1:],)).T
boundary_ranges[9,1] = 150

demand_mean_tot, demand_mean_allsim = extract_ranges_info(pathfold, 0, boundary_ranges, namefile )

#%% plot heatmap plot


name_simple = ['PV planned - ground', 'PV planned - roof', 'Wind planned - onshore', 'Wind planned - offshore',
                  'New heat pumps', 'Biomass boiler' , 'Oil boiler', 'GPL boiler', 'Battery']

if len(boundary_ranges)==10:
    x_axis_label = 'Costs ranges [M€]'
    save_name = 'SA_chess_dem_mon.png'
else:
    x_axis_label = 'Emissions ranges [MtonCO2]'
    save_name = 'SA_chess_dem_em.png'
    
colorbar_label = '% of total energy produced'

# Flatten the matrix to a 1D array and find unique values
unique_values = np.unique(boundary_ranges)

# Order the unique values
ordered_values = np.sort(unique_values)

# Invert the indexes and columns of the DataFrame
data_tot_cap_inverted = demand_mean_tot.transpose()*100

if len(boundary_ranges)!=10:
    data_tot_cap_inverted = data_tot_cap_inverted.iloc[:, ::-1]
    ordered_values = ordered_values[::-1]
    
fig, ax = plt.subplots(figsize=(15, 6), dpi = 300)

data_tot_cap_inverted.index = name_simple 


#change order of indexes 
index = ['PV planned - ground', 'PV planned - roof', 'Wind planned - onshore', 'Wind planned - offshore', 'Battery', 'New heat pumps', 'Biomass boiler',  'Oil boiler', 'GPL boiler']
data_tot_cap_inverted = data_tot_cap_inverted.reindex(index)


# Plot the DataFrame as a chessboard of gray colors
ax.imshow(data_tot_cap_inverted, cmap='gray_r', interpolation='none', vmin=0, vmax=50)

# Add numbers to each cell using annotate
for i in range(data_tot_cap_inverted.shape[0]):
    for j in range(data_tot_cap_inverted.round(1).shape[1]):
        plt.annotate(str(data_tot_cap_inverted.round(1).iloc[i, j]), fontsize=7 ,xy=(j, i), ha='center', va='center', color='red')


# Set the x-axis labels based on DataFrame indexes
ax.set_yticks(range(data_tot_cap_inverted.shape[0]), data_tot_cap_inverted.index)

# Set the x-axis ticks at the borders of the cells
ax.set_xticks(np.arange(-0.5, data_tot_cap_inverted.shape[1], 1), np.round(ordered_values,3))

# Add a colorbar on the right
cbar = plt.colorbar(ax.images[0], ax=ax, orientation='vertical', pad=0.05)
cbar.set_label(colorbar_label)

# Set the x-axis label
ax.set_xlabel(x_axis_label)

plt.savefig( 'SA_figures/' + save_name , dpi=250 ,  bbox_inches='tight')


#%% plot boxplot with ranges for electricity production

tech_plot = ['pv_planned_ground', 'pv_planned_roof', 'wind_planned_onshore', 'wind_planned_offshore']
box_colors = ['#b2b400', '#dde000', '#0083ff', '#00e8ff']
save_name = 'SA_ranges_dem_el.png'
             
#create DataFrame 
column_names = []

for i in range(len(boundary_ranges)):
    column_names.append(str(boundary_ranges[i,0]) + "-" + str(boundary_ranges[i,1]))

data_boxplot = pd.DataFrame(columns=column_names)

#for each scenario
for s in range(0,num_scenario):
    
    data_mean_s = demand_mean_allsim['scenario_'+str(s)][tech_plot].T
    data_mean_s.columns = data_boxplot.columns
    data_boxplot = data_boxplot.append(data_mean_s, ignore_index=False)
    
y_axis_label = '% of total energy produced'
x_axis_label = 'Costs ranges [M€]'
dfl = data_boxplot.stack().reset_index().rename(columns={'level_0':'tech','level_1': x_axis_label, 0: y_axis_label})

# Move rows containing the string "40-50" to the top
dfl = pd.concat([dfl[dfl[x_axis_label].str.contains('40-50')], dfl[~dfl[x_axis_label].str.contains('40-50')]])

# Reset index
dfl = dfl.reset_index(drop=True)

# Set the size of the figure
fig, ax = plt.subplots(figsize=(15, 6), dpi = 300)

# plot
# boxprops = dict(linewidth=0, edgecolor='None')
ax = sns.boxplot(x_axis_label, y_axis_label, data=dfl,hue='tech',fliersize = 2,
                 boxprops=dict(edgecolor='black'),whiskerprops=dict(color='gray'),  width=0.5, palette= box_colors, dodge = 1)

plt.legend(title='Technologies')

plt.savefig( 'SA_figures/' + save_name , dpi=250 ,  bbox_inches='tight')

#%% plot boxplot with ranges for heat production

import seaborn as sns

plot_id = 0

tech_plot = ['P2Heat_planned', 'supply_heat_solid' , 'supply_heat_oil', 'supply_heat_gpl', 'battery']
box_colors = ['#ff9b9b', '#b26912', '#3a3a47', '#7b74e8', '#bb0db3']
save_name = 'SA_ranges_dem_heat.png'
                      
#create DataFrame 
column_names = []

for i in range(len(boundary_ranges)):
    column_names.append(str(boundary_ranges[i,0]) + "-" + str(boundary_ranges[i,1]))

data_boxplot = pd.DataFrame(columns=column_names)

#for each scenario
for s in range(0,num_scenario):
    
    data_mean_s = demand_mean_allsim['scenario_'+str(s)][tech_plot].T
    data_mean_s.columns = data_boxplot.columns
    data_boxplot = data_boxplot.append(data_mean_s, ignore_index=False)
    
y_axis_label = '% of total energy produced'
x_axis_label = 'Costs ranges [M€]'
dfl = data_boxplot.stack().reset_index().rename(columns={'level_0':'tech','level_1': x_axis_label, 0: y_axis_label})

# Move rows containing the string "40-50" to the top
dfl = pd.concat([dfl[dfl[x_axis_label].str.contains('40-50')], dfl[~dfl[x_axis_label].str.contains('40-50')]])

# Reset index
dfl = dfl.reset_index(drop=True)

# Set the size of the figure
fig, ax = plt.subplots(figsize=(15, 6), dpi = 300)

# plot
# boxprops = dict(linewidth=0, edgecolor='None')
ax = sns.boxplot(x_axis_label, y_axis_label, data=dfl,hue='tech',fliersize = 2,
                 boxprops=dict(edgecolor='black'),whiskerprops=dict(color='gray'),  width=0.5, palette= box_colors, dodge = 1)

plt.legend(title='Technologies')

plt.savefig( 'SA_figures/' + save_name , dpi=250 ,  bbox_inches='tight')
