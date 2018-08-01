using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Solver
{
    public class Coloring
    {
        public void Run(string inputFile)
        {
            Console.WriteLine("Start Coloring solver...");

            //read input and create graph
            string[] inputs = File.ReadAllLines(inputFile);
            string[] line = inputs[0].Split(' ');

            Graph graph = new Graph();
            graph.nbnodes = Convert.ToInt32(line[0]);
            graph.nbedges = Convert.ToInt32(line[1]);
            Node snode = null;
            Node enode = null;

            for (int i = 0; i < graph.nbedges; i++)
            {
                line = inputs[i + 1].Split(' ');
                int id1 = Convert.ToInt16(line[0]);
                int id2 = Convert.ToInt16(line[1]);
                
                // add or get start node
                if (graph.nodes.ContainsKey(id1))
                {
                    snode = graph.nodes[id1];
                }
                else
                {
                    snode = new Node(id1);
                    graph.nodes.Add(id1, snode);
                }

                // add or get end node
                if (graph.nodes.ContainsKey(id2))
                {
                    enode = graph.nodes[id2];
                }
                else
                {
                    enode = new Node(id2);
                    graph.nodes.Add(id2, enode);
                }

                // add neighbors
                if (!snode.neighbors.ContainsKey(enode.id)) snode.neighbors.Add(enode.id, enode);
                if (!enode.neighbors.ContainsKey(snode.id)) enode.neighbors.Add(snode.id, snode);

                // add edge
                Edge edge = new Edge(snode, enode);
                if (!graph.edges.ContainsKey(edge.id)) graph.edges.Add(edge.id, edge);
            }

            bool end = true;
        }


    }

    public class Graph
    {
        public int nbnodes = 0;
        public int nbedges = 0;
        public Dictionary<int, Node> nodes = new Dictionary<int, Node>();
        public Dictionary<string, Edge> edges = new Dictionary<string, Edge>();



    }

    public class Node
    {
        public int id = 0;
        public Dictionary<int, Node> neighbors = new Dictionary<int, Node>();
        public Node(int id)
        {
            this.id = id;
        }
    }

    public class Edge
    {
        public string id = "";
        public Node snode;
        public Node enode;

        public Edge(Node snode, Node enode)
        {
            this.snode = snode;
            this.enode = enode;
            this.id = this.snode.id.ToString() + "_" + this.enode.id.ToString();
        }
    }

}
