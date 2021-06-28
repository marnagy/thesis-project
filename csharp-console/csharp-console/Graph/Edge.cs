using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace csharp_console.Graph
{
	public class Edge
	{
		[JsonProperty("start_node_id")]
		public ulong StartNodeId { get; set; }
		[JsonProperty("dest_node_id")]
		public ulong EndNodeId { get; set; }
		[JsonProperty("length")]
		public double Length { get; set; }
		[JsonProperty("travel_time")]
		public double TravelTime { get; set; }

	}
}
