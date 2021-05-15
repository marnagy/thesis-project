using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace csharp_console
{
	public class Config
	{
		public int WarehousesAmount { get; set; }
		public int[] CarsAmount { get; set; }
		public int NGen { get; set; } = 50;
		public int PopulationSize { get; set; } = 10;
		public double WarehouseMutProb { get; set; }
		public double PointWarehouseMutProb { get; set; }
		public double RouteMutProb { get; set; }
		public int Runs { get; set; } = 10;
		public int MaxParallelRequests { get; set; } = 5;
		public string ServerHost { get; set; } = "localhost";
		public int ServerPort { get; set; } = 5_000;
		public static Config FromJson(string configFile)
		{
			string text = File.ReadAllText(configFile);
			var config = JsonConvert.DeserializeObject<Config>(text);
			return config;
		}
        public override string ToString()
        {
            return JsonConvert.SerializeObject(this);
        }
    
	}
}
