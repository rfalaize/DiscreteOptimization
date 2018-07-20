using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Solver
{
    class Program
    {
        static void Main(string[] args)
        {
            try
            {
                string problemName = args[0];
                string inputFile = args[1];
                switch (problemName)
                {
                    case "knapsack":
                        Knapsack.Run(inputFile);
                        break;
                }
            }
            catch (Exception e)
            {
                Console.WriteLine(e);
            }
        }
    }
}
