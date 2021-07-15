using System;
using System.Collections.Generic;
//using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console.Graph
{
	public class ReadOnlyGraph
	{
		public readonly IReadOnlyDictionary<ulong, ReadOnlyNode> Nodes;

		public ReadOnlyGraph(IReadOnlyList<ReadOnlyNode> nodes)
		{
			var tempDict = new Dictionary<ulong, ReadOnlyNode>(nodes.Count);
			foreach (var node in nodes)
			{
				tempDict.Add(node.Id, node);
			}
			Nodes = tempDict;
		}

		public double AStar(PointD p1, PointD p2, string weight)
		{
			var startNode = MapToClosest(p1);
			var endNode = MapToClosest(p2);

			var visitedIds = new HashSet<ulong>();
			var activeEdges = new Heap<(double edgeValue, double edgeWeightValue, ReadOnlyEdge edge)>(
				(e1, e2) => Math.Sign(e1.edgeValue - e2.edgeValue)
			);
			foreach (var outEdge in startNode.OutEdges)
			{
				var w = outEdge.Weights[weight];
				activeEdges.Add( ( w + Distance(outEdge.EndNodeId, endNode.Id), w, outEdge) ) ;
			}

			while ( activeEdges.Count > 0)
			{
				(double edgeValue, double edgeWeightValue, ReadOnlyEdge e) = activeEdges.Get();

				if ( visitedIds.Contains( e.EndNodeId ) )
					continue;

				if (e.EndNodeId == endNode.Id)
					return edgeWeightValue;

				var node = Nodes[e.EndNodeId];
				visitedIds.Add(node.Id);

				foreach (var edge in node.OutEdges)
				{
					if ( !visitedIds.Contains( edge.EndNodeId ))
					{
						var w = edge.Weights[weight] + edgeWeightValue;
						activeEdges.Add( (w + Distance(edge.EndNodeId, endNode.Id), w, edge) );
					}
				}

			}
			return double.PositiveInfinity;
		}

		public double Dijkstra(PointD p1, PointD p2, string weight)
		{
			var startNode = MapToClosest(p1);
			var endNode = MapToClosest(p2);

			var visitedIds = new HashSet<ulong>();
			var activeEdges = new Heap<(double edgeWeightValue, ReadOnlyEdge edge)>(
				(e1, e2) => Math.Sign(e1.edgeWeightValue - e2.edgeWeightValue)
			);
			foreach (var outEdge in startNode.OutEdges)
			{
				var w = outEdge.Weights[weight];
				activeEdges.Add( (w, outEdge) ) ;
			}

			while ( activeEdges.Count > 0)
			{
				(double edgeWeightValue, ReadOnlyEdge e) = activeEdges.Get();

				if ( visitedIds.Contains( e.EndNodeId ) )
					continue;

				if (e.EndNodeId == endNode.Id)
					return edgeWeightValue;

				var node = Nodes[e.EndNodeId];
				visitedIds.Add(node.Id);

				foreach (var edge in node.OutEdges)
				{
					if ( !visitedIds.Contains( edge.EndNodeId ))
					{
						var w = edge.Weights[weight] + edgeWeightValue;
						activeEdges.Add( (w, edge) );
					}
				}

			}
			return double.PositiveInfinity;
		}
		/// <summary>
		/// Map to closest node using euklidian metric function.
		/// </summary>
		/// <param name="p"></param>
		/// <returns></returns>
		public ReadOnlyNode MapToClosest(PointD p)
		{
			double closestNodeDistance = double.PositiveInfinity;
			ReadOnlyNode closestNode = null;
			foreach (var node in Nodes.Values)
			{
				double distance = Distance(p, node.Point);
				if ( distance < closestNodeDistance)
				{
					closestNodeDistance = distance;
					closestNode = node;
				}
			}
			return closestNode;
		}
		private double Distance(PointD p1, PointD p2)
		{
			return Math.Sqrt( (p1.X - p2.X)*(p1.X - p2.X) + (p1.Y - p2.Y)*(p1.Y - p2.Y) );
		}
		private double Distance(ulong id1, ulong id2)
		{
			return Distance(Nodes[id1].Point, Nodes[id2].Point);
		}
	}
}
