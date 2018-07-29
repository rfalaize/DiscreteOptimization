#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

def LogInfo(msg):
    print(datetime.now().strftime('%H:%M:%S') + ' - ' + msg)

def ReadFile(file_location):
    with open(file_location, 'r') as input_data_file:
        input_data = input_data_file.read()
    return input_data

def GetInputs(input_data):
    input_data = input_data.splitlines()
    input_data = [list(map(int, x.split(' ')))  for x in input_data]
    inputs={}
    inputs['nbnodes'] = input_data[0][0]
    inputs['nbedges'] = input_data[0][1]
    inputs['startnodes'] = [row[0] for row in input_data[1:]]
    inputs['endnodes'] = [row[1] for row in input_data[1:]]
    adjacentnodes = {}
    for row in input_data[1:]:
        node1 = row[0]
        node2 = row[1]
        if node1 not in adjacentnodes:
            adjacentnodes[node1] = []
        if node2 not in adjacentnodes[node1]:
            adjacentnodes[node1].append(node2)
        if node2 not in adjacentnodes:
            adjacentnodes[node2] = []
        if node1 not in adjacentnodes[node2]:
            adjacentnodes[node2].append(node1)
    for k, v in adjacentnodes.items():
        v.sort()
    inputs['nodes'] = list(adjacentnodes.keys())
    inputs['colors'] = range(len(inputs['nodes'])) # initialize colors to one for each node
    inputs['adjacentnodes'] = adjacentnodes
    return inputs

def RunGreedyAlgorithm(inputNodes, inputs):
    nodecolors = {}

    # loop on each node
    for node in inputs['nodes']:
        #print('>> Node ', node)
        for color in inputs['colors']:
            #print('    >> Color ', color)
            # try to assign each color until one is valid
            # to determine if a color is valid, we look at all adjacent nodes and discard already assigned colors.
            isAvailable = True

            if node not in inputs['adjacentnodes']:
                # if the node doesn't have any adjacent nodes, assign the first available color
                print('does not have any neighboors')
                nodecolors[node] = color
                break

            adjacentNodes = inputs['adjacentnodes'][node]
            for adjacentNode in adjacentNodes:
                if adjacentNode in nodecolors:
                    # if the node already has a color assigned ...
                    if nodecolors[adjacentNode] == color:
                        # ... and if the color assigned is the same than the current one, discard it.
                        isAvailable = False
                        break

            if isAvailable:
                nodecolors[node] = color
                break

    output = {}
    output['objective'] = len(set(nodecolors.values()))
    output['variables'] = list(nodecolors.values())
    return output

def RunSolver(inputs):
    from ortools.constraint_solver import pywrapcp

    # Creates the solver
    solver = pywrapcp.Solver("GraphColoring")

    # run greedy algorithm first, to find an upper bound on the number of required colors
    greedyoutputs = RunGreedyAlgorithm(inputs['nodes'], inputs)
    print('Greedy objective: ', greedyoutputs['objective'])
		
    # Creates the variables
    variables = []
    for i in range(inputs['nbnodes']):
        # x = solver.IntVar(0, inputs['nbnodes'] - 1, "x" + str(i))
        x = solver.IntVar(0, greedyoutputs['objective'] - 1, "x" + str(i))
        variables.append(x)

    # Create the constraints
    for edge in range(inputs['nbedges']):
        # get variables corresponding to start and end nodes
        snode = inputs['startnodes'][edge]
        enode = inputs['endnodes'][edge]
        #print('Adding constraint: ', snode, ' != ', enode)
        xs = variables[snode]
        xe = variables[enode]
        solver.Add(xs != xe)
        
    # Create the decision builder
    db = solver.Phase(variables, solver.CHOOSE_FIRST_UNBOUND, solver.ASSIGN_MIN_VALUE)

    # Start solving
    starttime = datetime.now()
    solver.Solve(db)

    count = 0
    outputs = {}
    while solver.NextSolution():
        count += 1
        # get variable values
        results = []
        for x in variables:
            results.append(x.Value())
        objective = len(set(results))
        if outputs == {}:
            outputs['objective'] = objective
            outputs['variables'] = results
        elif objective < outputs['objective']:
            outputs['objective'] = objective
            outputs['variables'] = results
        if (count % 100000) == 0:
            LogInfo("Solution " + str(count) + '; objective=' + str(outputs['objective']))

    print('Run took ' + str(datetime.now() - starttime))
    print(count, ' solutions scanned.')
    return outputs

def RunLinearSolver(inputs):
    from ortools.linear_solver import pywraplp

    solver = pywraplp.Solver('GraphColoringSolver', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    # Objective function: minimize y (cap)
    objective = solver.Objective()
    objective.SetMinimization()

    # Constraints
    # ************************************************************

    # constraint 1): cap
    # Add an artifical cap variable, y, that will be superior to the maximum color of the graph.
    # Minimizing y will squash the max color to its minimal possible value, which is 
    # equivalent to finding the optimal graph coloring. 
    constraint_cap = solver.Constraint(0, solver.infinity()) 

    # Variables
    y = solver.IntVar(0.0, inputs['nbnodes'], 'y')
    constraint_cap.SetCoefficient(y, 1)
    objective.SetCoefficient(y, 1)

    variables = []
    for n in range(inputs['nbnodes']):
        # constraint 2): each node must be assigned a unique color
        constraint_unique_node_color = solver.Constraint(1, 1)
        variables_colors = []
        for c in inputs['colors']:
            # add one variable for each {node+color} pairs
            x = solver.BoolVar('x_n' + str(n) + '_c' + str(c))
            variables_colors.append(x)
            # add to constraint 1)
            constraint_cap.SetCoefficient(x, (-1)*c)
            # add to constraint 2)
            constraint_unique_node_color.SetCoefficient(x, 1)
        variables.append(variables_colors)

    # constraint 3): adjacent nodes cannot have the same color
    for e in range(inputs['nbedges']):
        for c in inputs['colors']:
            #print('Add constraint: color ', c, ': ', inputs['startnodes'][e], ' != ', inputs['endnodes'][e])
            constraint_adj_nodes = solver.Constraint(0, 1) 
            constraint_adj_nodes.SetCoefficient(variables[inputs['startnodes'][e]][c], 1)
            constraint_adj_nodes.SetCoefficient(variables[inputs['endnodes'][e]][c], 1)
    
    # Solve
    LogInfo('Start solving...')
    solver.Solve()
    LogInfo('Solver finished.')
    
    results = []
    for n in range(inputs['nbnodes']):
        results.append(-1)
        for c in inputs['colors']:
            # print('node ', n, ', color ', c, ': ', )
            if 1 == variables[n][c].solution_value():
                results[n] = int(c)
                break
    # objectiveValue = objective.Value()
    objectiveValue = max(results)

    # Results
    print('Number of variables =', solver.NumVariables())
    print('Number of constraints =', solver.NumConstraints())
    print('x = ', results)
    print('Optimal objective value =', objectiveValue)

    outputs = {}
    outputs['objective'] = int(objectiveValue)
    outputs['variables'] = results
    return outputs
    
def solve_it(input_data):
    # Modify this code to run your optimization algorithm

    # parse the input
    inputs = GetInputs(input_data)

    #greedyoutputs = RunGreedyAlgorithm(inputs['nodes'], inputs)
    #outputs = greedyoutputs
    #outputs = RunSolver(inputs)
    outputs = RunLinearSolver(inputs)
    
    # prepare the solution in the specified output format
    output_data = str(outputs['objective']) + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, outputs['variables'])) 
    return output_data


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/gc_4_1)')

