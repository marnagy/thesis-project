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
			foreach (var node in Nodes)
			{
				nodes.Add(
					new ReadOnlyNode(
						node.Id,
						new PointD(node.Latitude, node.Longitude),
						Edges.Where(e => e.StartNodeId == node.Id)
							.Select(e => new ReadOnlyEdge(e))
							.ToHashSet()
					)
				);
			}
			return new ReadOnlyGraph(nodes);
		}
	}
}
