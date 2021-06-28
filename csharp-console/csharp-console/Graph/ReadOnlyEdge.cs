using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console.Graph
{
	public class ReadOnlyEdge
	{
		public readonly ulong StartNodeId;
		public readonly ulong EndNodeId;
		public readonly IReadOnlyDictionary<string, double> Weights;

		public ReadOnlyEdge(Edge e)
		{
			StartNodeId = e.StartNodeId;
			EndNodeId = e.EndNodeId;
			var w = new Dictionary<string, double>(2);
			w.Add("length", e.Length);
			w.Add("travel_time", e.TravelTime);
			Weights = w;
		}
	}
}
