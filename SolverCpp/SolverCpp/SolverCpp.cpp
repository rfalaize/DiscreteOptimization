#include "stdafx.h"
#include "ortools/linear_solver/linear_solver.h"
#include "ortools/linear_solver/linear_solver.pb.h"
#include <iostream>

using namespace std;

namespace operations_research {
	void RunTest(MPSolver::OptimizationProblemType optimization_problem_type)
	{
		MPSolver solver("Glop", optimization_problem_type);
		MPVariable* const x = solver.MakeNumVar(0.0, 1, "x");
		MPVariable* const y = solver.MakeNumVar(0.0, 2, "y");
		MPObjective* const objective = solver.MutableObjective();
		objective->SetCoefficient(x, 1);
		objective->SetCoefficient(y, 1);
		objective->SetMaximization();
		solver.Solve();
		printf("\nSolution:");
		printf("\nx = %.1f", x->solution_value());
		printf("\ny = %.1f", y->solution_value());
	}

	void RunExample() {
		printf("Start program...");
		RunTest(MPSolver::GLOP_LINEAR_PROGRAMMING);
		printf("Press any key to return... ");
		cin;
	}
}

int main(int argc, char** argv) {
	operations_research::RunExample();
	return 0;
}

