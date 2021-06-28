using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console.Graph
{
	public class Node
	{
		[JsonProperty("id")]
		public ulong Id { get; set; }
		[JsonProperty("lat")]
		public double Latitude { get; set; }
		[JsonProperty("lon")]
		public double Longitude { get; set; }
	}
}
