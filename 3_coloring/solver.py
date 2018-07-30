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
    minColors = 1
    maxColors = 0
    uboundColors = 1 + len(neighbors)
    for n in neighbors:
        neighborsneighbors = inputs['adjacentnodes'][n]
        for c in range(1, uboundColors):
            isAvailable = True
            for nn in neighborsneighbors:
                # if the neighbor's neighbor is already assigned to color c,
                # then flag it as unavailable
                if nn in neighborsColors:
                    if neighborsColors[nn] == c:
                        isAvailable = False
                        break
            if isAvailable:
                neighborsColors[n] = c
                if c > maxColors:
                    maxColors = c
                # print('color ', c, ' assigned to neighbor ', n)
                break
    return maxColors + 1

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
        # constraint 1): each node must be assigned a unique color
        constraint_unique_node_color = solver.Constraint(1, 1)
        variables_colors = []
        for c in colorsrange:
            # add one variable for each {node+color} pairs
            x = solver.BoolVar('x_n' + str(n) + '_c' + str(c))
            variables_colors.append(x)
            # constraint 2): cap
            # Add an artifical cap variable, y, that will be superior to the maximum color of the graph.
            # Minimizing y will squash the max color to its minimal possible value, 
            # which is equivalent to finding the optimal graph coloring. 
            # By making y superior to each color value, we make y superior to the maximum color.
            constraint_cap = solver.Constraint(0, solver.infinity()) 
            constraint_cap.SetCoefficient(y, 1)
            constraint_cap.SetCoefficient(x, (-1)*c)
            # add to constraint 1)
            constraint_unique_node_color.SetCoefficient(x, 1)
        variables.append(variables_colors)

    LogInfo('Add constraints on adjacent nodes...')
    # constraint 3): adjacent nodes cannot have the same color
    for e in range(inputs['nbedges']):
        if (e % 10000) == 0:
            LogInfo('Adding constraint on edge ' + str(e) + '...')
        startnodevariables = variables[inputs['startnodes'][e]]
        endnodevariables = variables[inputs['endnodes'][e]]
        for c in colorsrange:
            #print('Add constraint: color ', c, ': ', inputs['startnodes'][e], ' != ', inputs['endnodes'][e])
            constraint_adj_nodes = solver.Constraint(0, 1) 
            constraint_adj_nodes.SetCoefficient(startnodevariables[c], 1)
            constraint_adj_nodes.SetCoefficient(endnodevariables[c], 1)
        
    # Solve
    LogInfo('Start solving...')
    solver.Solve()
    LogInfo('Solver finished.')
        
    results = []
    for n in range(inputs['nbnodes']):
        results.append(-1)
        for c in colorsrange:
            # print('node ', n, ', color ', c, ': ', )
            if 1 == variables[n][c].solution_value():
                results[n] = int(c)
                break
    LogInfo('Objective value of y=' + str(objective.Value()))
    objectiveValue = max(results) + 1

    # Results
    LogInfo('Number of variables =' + str(solver.NumVariables()))
    LogInfo('Number of constraints =' + str(solver.NumConstraints()))
    LogInfo('Variables values = ' + str(results))
    LogInfo('Optimal objective value =' + str(objectiveValue))

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

