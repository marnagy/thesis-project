using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console
{
	/// <summary>
	/// Singleton class for more performance on client and to reduce the amount of requests to server.
	/// Singleton version of DBService.
	/// </summary>
	public class FitnessWithProxy
	{
		private static FitnessWithProxy instance = null;
		private static object _lock = new object();
		public static FitnessWithProxy GetInstance()
		{
			if (instance is null)
			{
				lock (_lock)
				{
					if (instance is null)
						instance = new FitnessWithProxy();
				}
			}
			
			return instance;
		}
		readonly ConcurrentDictionary<(PointD, PointD), double> timeDB;
		readonly ConcurrentDictionary<(PointD, PointD), double> distanceDB;
		private FitnessWithProxy()
		{
			timeDB = new ConcurrentDictionary<(PointD, PointD), double>();
			distanceDB = new ConcurrentDictionary<(PointD, PointD), double>();
		}
		public bool TryGetFitness(PointD p1, PointD p2, Mode mode, out double res)
		{
			return mode == Mode.Time ? timeDB.TryGetValue((p1, p2), out res)
				: distanceDB.TryGetValue((p1, p2), out res );
		}
		public bool TryAddValue(PointD p1, PointD p2, Mode mode, double value)
		{
			return mode == Mode.Time ? timeDB.TryAdd((p1, p2), value)
				: distanceDB.TryAdd((p1, p2), value);
		}
		public async Task<double> FitnessFunc(PointD p1, PointD p2, Mode mode)
		{
			if ( this.TryGetFitness(p1, p2, mode, out double value) )
			{
				return value;
			}
			else
			{
				var val = Evaluation.MapDistance(p1, p2, mode);
				this.TryAddValue(p1, p2, mode, val);
				return val;
			}
		}
	}
}
