#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from subprocess import Popen, PIPE

def solve_it(input_data):

    print("Writes the inputData to a temporay file...")
    tmp_input_file_name = 'input.txt'
    tmp_input_file = open(tmp_input_file_name, 'w')
    tmp_input_file.write(input_data)
    tmp_input_file.close()

    print("Start slave solver process...")
    process = Popen(['C:/Users/rhome/github/DiscreteOptimization/Solver/Solver/bin/x64/Release/Solver.exe', 'knapsack', tmp_input_file_name], stdout=PIPE)
    (stdout, stderr) = process.communicate()

    print("Get results...")
    tmp_output_file_name = 'output.txt'
    tmp_output_file = open(tmp_output_file_name, 'r')
    results = tmp_output_file.read()
    print("Results:")
    print("***************************************************************")
    print(results)
    print("***************************************************************")
    tmp_output_file.close()

    # removes the temporay files
    os.remove(tmp_input_file_name)
    os.remove(tmp_output_file_name)
		
    return results


import sys

if __name__ == '__main__':
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print("Input data:")
        print("***************************************************************")
        print(input_data)
        print("***************************************************************")
        solve_it(input_data)
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/ks_4_0)')
