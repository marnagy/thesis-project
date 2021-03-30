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
	public static class DBService
	{
		//static readonly SQLiteConnection db;
		static readonly ConcurrentDictionary<(PointD, PointD), double> db;
		static DBService()
		{
			db = new ConcurrentDictionary<(PointD, PointD), double>();
		}
		//private static SQLiteConnection CreateConnection()
		//{

		//}
		public static bool TryGetFitness(PointD p1, PointD p2, out double res)
		{
			return db.TryGetValue((p1, p2), out res);
		}
		public static void AddValue(PointD p1, PointD p2, double value)
		{
			db.TryAdd((p1, p2), value);
		}
	}
}
