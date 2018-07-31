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
    LogInfo('nbnodes=' + str(inputs['nbnodes']) + '; nbedges=' + str(inputs['nbedges']))
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

# function to get the lower bounds of possible colors
# example: GetGraphColoringLowerBound(GetInputs(ReadFile('data/a_4')), 0)
def GetGraphColoringLowerBound(inputs, node):
    neighbors = inputs['adjacentnodes'][node]
    # print('neighbors of ', node, ': ',neighbors)
    neighborsColors = {}
    minColors = 0
    for n in neighbors:
        neighborsneighbors = inputs['adjacentnodes'][n]
        commonneighbors = 0
        for nn in neighborsneighbors:
            if nn != node: 
                if nn in neighbors:
                    commonneighbors += 1
                if commonneighbors > minColors:
                    minColors = commonneighbors
    return minColors + 1

# function to run the algorithm for a given, ordered, list of nodes 
def RunGreedyAlgorithm(inputs):
    LogInfo('Start greedy algo...')
    nodecolors = {}

    inputNodes = inputs['nodes']
    
    # sort nodes based on their number of neighbors.
    # nodes with more neighbors will have priority during color assignment
    LogInfo('Sorting nodes...')
    sortedNodesDict = {}
    maxneighbors = 0
    for k, v in inputs['adjacentnodes'].items():
        nbneighbors = len(v)
        sortedNodesDict[k] = nbneighbors
    sortedNodesDict = sorted(sortedNodesDict.items(), key=lambda x: x[1])
    sortedNodes = []
    for n in sortedNodesDict:
        sortedNodes.append(n[0])
    sortedNodes = sortedNodes[::-1]
    inputNodes = sortedNodes

    # get lower bound on color number
    LogInfo('Searching lower bound...')
    lbound = 0
    for n in inputNodes:
        nlbound = GetGraphColoringLowerBound(inputs, n)
        if nlbound > lbound:
            lbound = nlbound
    LogInfo('Lower bound found: ' + str(lbound))
    
    LogInfo('Loop on each node...')
    for node in inputNodes:
        #print('>> Node ', node)
        for color in inputs['colors']:
            #print('    >> Color ', color)
            # try to assign each color until one is valid
            # to determine if a color is valid, we look at all adjacent nodes and discard already assigned colors.
            isAvailable = True

            if node not in inputs['adjacentnodes']:
                # if the node doesn't have any adjacent nodes, assign the first available color
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
    output['mincolors'] = lbound
    return output

def RunSolver(inputs):
    from ortools.linear_solver import pywraplp

    solver = pywraplp.Solver('GraphColoringSolver', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    # Run greedy algorithm first to determine lower and upper bound on the number of colors,
    # in order to reduce the search space
    greedyoutputs = RunGreedyAlgorithm(inputs)
    mincolors = 0
    maxcolors = greedyoutputs['objective']
    colorsrange = range(maxcolors)
    LogInfo('Greedy outputs: mincolors=' + str(mincolors) + '; maxcolors=' + str(maxcolors))

    # Objective function: minimize y (cap)
    objective = solver.Objective()
    objective.SetMinimization()

    # Variables
    y = solver.IntVar(mincolors, maxcolors, 'y')
    objective.SetCoefficient(y, 1)

    LogInfo('Add variables...')
    variables = []
    for n in range(inputs['nbnodes']):
        x = solver.IntVar(0.0, maxcolors, 'x_' + str(n))
        constraint_cap = solver.Constraint(0, solver.infinity()) 
        constraint_cap.SetCoefficient(y, 1)
        constraint_cap.SetCoefficient(x, (-1))
        variables.append(x)

    LogInfo('Add constraints on adjacent nodes...')
    epsilon = 0.1    # small value
    M = 10000        # large value
    for e in range(inputs['nbedges']):
        xs = variables[inputs['startnodes'][e]]
        xe = variables[inputs['endnodes'][e]]
        z = solver.BoolVar('xe_' + str(e))
        
        # artificial constraints to linearize inequalities xs <> xe 
        # (start node <> end node for each edge):
        # (1): xs - xe <= (-1)*epsilon + M*z
        # (2): xs - xe >= epsilon - (1-z)*M
        # is equivalent to
        # (1): xs - xe - M*z <= (-1)*epsilon
        # (2): xs - xe - M*z >= epsilon - M
        
        constraint_linearization_1 = solver.Constraint((-1)*solver.infinity(), (-1)*epsilon)
        constraint_linearization_1.SetCoefficient(xs, 1.0)
        constraint_linearization_1.SetCoefficient(xe, -1.0)
        constraint_linearization_1.SetCoefficient(z, (-1.0)*M)
        
        constraint_linearization_2 = solver.Constraint(epsilon - M, solver.infinity())
        constraint_linearization_2.SetCoefficient(xs, 1)
        constraint_linearization_2.SetCoefficient(xe, -1)
        constraint_linearization_2.SetCoefficient(z, (-1)*M)
        
    # Solve
    LogInfo('Number of variables =' + str(solver.NumVariables()))
    LogInfo('Number of constraints =' + str(solver.NumConstraints()))
    LogInfo('Start solving...')
    solver.Solve()
    LogInfo('Solver finished.')
        
    results = []
    for n in range(inputs['nbnodes']):
        results.append(variables[n].solution_value())

    print('Objective value of y=',objective.Value())
    objectiveValue = max(results) + 1

    # Results
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
    outputs = RunSolver(inputs)
    
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

