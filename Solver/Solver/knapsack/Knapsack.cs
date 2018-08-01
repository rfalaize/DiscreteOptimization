using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Google.OrTools.LinearSolver;
using System.Threading;

namespace Solver
{
    public class Knapsack
    {
        public static void Run(string inputFile)
        {
            Console.WriteLine("Start Knapsack solver...");

            //read input
            string[] inputs = File.ReadAllLines(inputFile);
            string[] line = inputs[0].Split(' ');

            int N = Convert.ToInt32(line[0]); // number of objects to pick from
            int K = Convert.ToInt32(line[1]); // capacity of the sack

            //create solver
            // GLOP_LINEAR_PROGRAMMING, CBC_MIXED_INTEGER_PROGRAMMING
            Google.OrTools.LinearSolver.Solver solver 
                = Google.OrTools.LinearSolver.Solver.CreateSolver("knapsack", "CBC_MIXED_INTEGER_PROGRAMMING");

            //objective
            Objective objective = solver.Objective();
            
            objective.SetMaximization();

            //variables
            Variable[] variables = solver.MakeBoolVarArray(N);

            //constraints
            Constraint capacityConstraint = solver.MakeConstraint(0, K);

            for (int i = 0; i < N; i++)
            {
                //get input parameters
                line = inputs[i + 1].Split(' ');
                double value = Convert.ToDouble(line[0]);
                double weight = Convert.ToDouble(line[1]);

                Variable x = variables[i];

                //add to objective
                objective.SetCoefficient(x, value);

                //add to constraint
                capacityConstraint.SetCoefficient(x, weight);
            }

            MPSolverParameters solverParams = new MPSolverParameters();

            Console.WriteLine("Start solving...");
            int resultStatus = solver.Solve();
            
            double resultObjective = 0.0;
            string resultVariables = "";

            Console.WriteLine("Solver finished");
            Console.WriteLine("Solution status: " + resultStatus.ToString());
            
            string outputFile = new FileInfo(inputFile).Directory.FullName + @"\output.txt";
            if (File.Exists(outputFile)) File.Delete(outputFile);

            if (resultStatus != Google.OrTools.LinearSolver.Solver.OPTIMAL)
            {
                resultStatus = 0;
                Console.WriteLine("The problem don't have an optimal solution.");
            }
            else
            {
                resultStatus = 1;
                Console.WriteLine("Solution objective: " + solver.Objective().Value().ToString());
                resultObjective = solver.Objective().Value();

                foreach (Variable x in variables)
                {
                    if (resultVariables == "")
                        resultVariables = x.SolutionValue().ToString();
                    else
                        resultVariables += " " + x.SolutionValue().ToString();
                }
                Console.WriteLine("Solution variables: " + resultVariables.ToString());
            }
            
            using (System.IO.StreamWriter file = new System.IO.StreamWriter(outputFile))
            {
                file.WriteLine(resultObjective.ToString() + " " + resultStatus.ToString());
                file.WriteLine(resultVariables);
            }
        }
    }
}
