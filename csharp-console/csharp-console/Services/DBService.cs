using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console.Services
{
	/// <summary>
	/// Singleton class for more performance on client and to reduce the amount of requests to server.
	/// </summary>
	// public static class DBService
	// {
	// 	static readonly ConcurrentDictionary<(PointD, PointD), double> timeDB;
	// 	static readonly ConcurrentDictionary<(PointD, PointD), double> distanceDB;
	// 	static DBService()
	// 	{
	// 		timeDB = new ConcurrentDictionary<(PointD, PointD), double>();
	// 		distanceDB = new ConcurrentDictionary<(PointD, PointD), double>();
	// 	}
	// 	public static bool TryGetFitness(PointD p1, PointD p2, Mode mode, out double res)
	// 	{
	// 		return mode == Mode.Time ? timeDB.TryGetValue((p1, p2), out res)
	// 			: distanceDB.TryGetValue((p1, p2), out res );
	// 	}
	// 	public static bool TryAddValue(PointD p1, PointD p2, Mode mode, double value)
	// 	{
	// 		return mode == Mode.Time ? timeDB.TryAdd((p1, p2), value)
	// 			: distanceDB.TryAdd((p1, p2), value);
	// 	}
	// }
}
