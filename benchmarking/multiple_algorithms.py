from platypus import *
import numpy as np
import os
import time
#from matplotlib import pyplot as plt

# Delete log file if existing
try:
    os.remove("log2.log")
except:
    pass

# Set the log file
logging.basicConfig(filename='log2.log', encoding='utf-8', level=logging.INFO)

# Set optimization class
class optimize_calliope_MA(Problem):
    
    def __init__(self):
        
        # Set feasibility set for the parameters
        super().__init__(3, 4)
        self.types[:] = [Real(0, 3), Real(0, 30),
                            Real(0, 3)]


    def evaluate(self, solution):
        start_fun = time.time()

        # Extract the parameter values generated by the evolutionary algorithms
        mv_1 = solution.variables[0]
        mv_2 = solution.variables[1]
        mv_3 = solution.variables[2]
        
        # Execute the model
        output = os.popen(f"python model_calliope_multi.py {mv_1} {mv_2} {mv_3}").read()[1:-2]
        
        # Convert to float
        output = output.replace(" ", "").split(",")
        objs = []
        for obj in output:
            objs.append(float(obj))

        # Update the solution
        solution.objectives[:] = np.array(objs)
        # print("Solution: " + str(solution.objectives[:]) + ", time: {:.4f}".format((time.time() - start_fun)))


if __name__ == '__main__':
    # Define the problem
    problem = optimize_calliope_MA()

    # List the algorithms
    algorithms = [
        NSGAII,
        (NSGAIII, {"divisions_outer":12}),
        #(CMAES, {"epsilons": [3000000/2, 6000000/2, 8000000/2, 1000000/2]}),
        GDE3,
        #IBEA,
        #(MOEAD, {"weight_generator":normal_boundary_weights, "divisions_outer":12}),
        (OMOPSO, {"epsilons": [3000000/2, 6000000/2, 8000000/2, 1000000/2]}),
        SMPSO,
        #SPEA2,
        (EpsMOEA, {"epsilons": [3000000/2, 6000000/2, 8000000/2, 1000000/2]})
    ]
    
    # Run in parallel
    with ProcessPoolEvaluator(20) as evaluator:
        results = experiment(algorithms, problem, seeds=2, nfe=1000, evaluator=evaluator)

    # Save the results
    for j, algorithm in enumerate(results.keys()):

        c = results[algorithm]["optimize_calliope_EpsMOEA"]

        xo = []
        xt = []
        for result in c:
            nondominated_solutions = nondominated(result)
        
            obj = np.ndarray(shape = (len(nondominated_solutions), 4)) # obj
            theta = np.ndarray(shape = (len(nondominated_solutions), 3)) # par

            i = 0
            for solution in nondominated_solutions:
                obj[i, :] = solution.objectives[:]
                theta[i, :] = solution.variables[:]
                i  = i + 1
            xo.append(obj)
            xt.append(theta)
        
        o = np.concatenate(xo, axis=0)
        t = np.concatenate(xt, axis = 0)
        
        np.savetxt(f'./results/obj_seeds3_{algorithm}.txt', o)
        np.savetxt(f'./results/theta_seeds3_{algorithm}.txt', t)