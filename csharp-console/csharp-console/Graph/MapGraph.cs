using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using csharp_console.Graph;

namespace csharp_console
{
	public class MapGraph
	{
		[JsonProperty("nodes")]
		public Node[] Nodes { get; set; }
		[JsonProperty("edges")]
		public Edge[] Edges { get; set; }
		public ReadOnlyGraph ToReadOnly()
		{
			var nodes = new List<ReadOnlyNode>(Nodes.Length);
			var edges = new Dictionary<ulong, HashSet<ReadOnlyEdge>>(nodes.Count);
			var emptySet = new HashSet<ReadOnlyEdge>();

			foreach (var edge in Edges)
			{
				if (edges.TryGetValue(edge.StartNodeId, out HashSet<ReadOnlyEdge> set))
				{
					set.Add( new ReadOnlyEdge(edge) );
				}
				else
				{
					var h = new HashSet<ReadOnlyEdge>
					{
						new ReadOnlyEdge(edge)
					};
					edges.Add(edge.StartNodeId, h);
				}
			}

			foreach (var node in Nodes)
			{
				nodes.Add(
					new ReadOnlyNode(
						node.Id,
						new PointD(node.Latitude, node.Longitude),
						edges.ContainsKey(node.Id) ? edges[node.Id] : emptySet
					)
				);
			}
			return new ReadOnlyGraph(nodes);
		}
	}
}
