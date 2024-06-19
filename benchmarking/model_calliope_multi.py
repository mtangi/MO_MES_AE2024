import calliope
import numpy as np
import sys

calliope.set_log_verbosity('error', include_solver_output=False)

mv_1 = sys.argv[1]
mv_2 = sys.argv[2]
mv_3 = sys.argv[3]

ph = 'model_sulcis_bench.yaml'
model = calliope.Model(ph)

model.run_config['objective_options']['cost_class']['emissions']=float(mv_1)
model.run_config['objective_options']['cost_class']['indipendence']= float(mv_2)
model.run_config['objective_options']['cost_class']['PM_emissions']=float(mv_3)

try:
    model.run()
    objs = model.get_formatted_array('cost').sum(['locs','techs']).to_pandas()    
    objs['monetary'] -=  objs['revenues'] 
    objs = list(objs[['monetary', 'emissions', 'indipendence', 'PM_emissions']])

except:
    objs = [np.power(10, 10), np.power(10, 10), np.power(10, 10), np.power(10, 10)]

print(objs)