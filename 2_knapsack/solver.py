#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
import sys
import os
from subprocess import Popen, PIPE
from ortools.linear_solver import pywraplp
from datetime import datetime

def GetInputs(input_data):
    input_data = input_data.splitlines()
    input_data = [list(map(int, x.split(' ')))  for x in input_data]
    inputs={}
    inputs['size'] = input_data[0][0]
    inputs['capacity'] = input_data[0][1]
    inputs['values'] = [row[0] for row in input_data[1:]]
    inputs['weights'] = [row[1] for row in input_data[1:]]
    return inputs

def LogInfo(msg):
    print(datetime.now().strftime('%H:%M:%S') + ' - ' + msg)
    
def SolveWithORToolsMIP(input_data):
    # Get inputs
    inputs = GetInputs(input_data)

    # Solver
    # options: GLOP_LINEAR_PROGRAMMING, CBC_MIXED_INTEGER_PROGRAMMING
    solver = pywraplp.Solver('KnapsackSolver', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    # Objective function: maximize the value of the knapsack
    objective = solver.Objective()
    objective.SetMaximization()

    # Constraint on capacity
    constraint = solver.Constraint(0, inputs['capacity'])
        
    # Variables
    variables = []
    for i in range(inputs['size']):
        x = solver.BoolVar('x' + str(i))
        variables.append(x)
        # add to constraint
        constraint.SetCoefficient(x, inputs['weights'][i])
        # add to objective
        objective.SetCoefficient(x, inputs['values'][i])

    # Solve
    LogInfo('Start solving...')
    solver.Solve()
    LogInfo('Solver finished.')

    results = []
    for i in range(inputs['size']):
        results.append(int(variables[i].solution_value()))
    objectiveValue = objective.Value()    

    # Results
    print('Number of variables =', solver.NumVariables())
    print('Number of constraints =', solver.NumConstraints())
    print('x = ', results)
    print('Optimal objective value =', objectiveValue)

    outputs = {}
    outputs['objective'] = int(objectiveValue)
    outputs['variables'] = results

    # Return
    results = str(outputs['objective']) + ' 0\n' + ' '.join(map(str, outputs['variables'])) 
    print('****************************************************')
    print(results)
    return results

def SolveWithORToolsBinPacking(input_data):
    # Get inputs
    inputs = GetInputs(input_data)
    # Create the solver
    from ortools.algorithms import pywrapknapsack_solver
    solver = pywrapknapsack_solver.KnapsackSolver(
        pywrapknapsack_solver.KnapsackSolver.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER,
        'knapsack')
    solver.Init(inputs['values'], [inputs['weights']], [inputs['capacity']])
    objectiveValue = solver.Solve()
    results = [int(solver.BestSolutionContains(x)) for x in range(inputs['size'])]
    objective = sum([x*v for x,v in zip(inputs['values'], results)])
    print('x = ', results)
    print('Optimal objective value =', objectiveValue)
    outputs = {}
    outputs['objective'] = int(objectiveValue)
    outputs['variables'] = results
    # Return
    results = str(outputs['objective']) + ' 1\n' + ' '.join(map(str, outputs['variables'])) 
    print('****************************************************')
    print(results)
    return results

def solve_it(input_data):
    #results = SolveWithORToolsMIP(input_data)
    results = SolveWithORToolsBinPacking(input_data)
    return results
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        solve_it(input_data)
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')
