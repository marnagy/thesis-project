using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using System.Diagnostics;
using Newtonsoft.Json;
using System.Threading;
using System.Collections.Concurrent;
using csharp_console.Graph;

namespace csharp_console
{
	public class Evaluation
	{
		public static readonly HttpClient client;
		public static string baseAddress { get; set; }
		static Semaphore _semaphore;
		static EvaluationMode EvalMode;
		static ReadOnlyGraph MapGraph;

		static Evaluation()
		{
			client = new HttpClient();
		}

		public static void StartManaging(int locks)
		{
			//_pool = new Semaphore(locks, locks*2);
			_semaphore = new Semaphore(locks, locks);
		}
		public static void SetEvaluationMode(EvaluationMode mode)
		{
			EvalMode = mode;
		}
		public static void SetMapGraph(ReadOnlyGraph mapGraph)
		{
			MapGraph = mapGraph;
		}

		private static double Request(string uri, string jsonArgument)
		{
			if (string.IsNullOrEmpty(uri)){
				throw new ArgumentException($"Wrong URI: {uri}");
			}

			var req = new HttpRequestMessage(HttpMethod.Get, uri);

			double result = 0;
			string content = null;
			try{
				var temp1 = client.GetAsync(uri);
				temp1.Wait();
				var response = temp1.Result;

				var temp2 = response.Content.ReadAsStringAsync();
				temp2.Wait();
				content = temp2.Result;
				var json = JsonConvert.DeserializeObject<Dictionary<string, double>>(content);
				result = json[jsonArgument];
			}
			catch (JsonReaderException e)
			{
				System.Console.WriteLine($"uri: {uri}");
				System.Console.WriteLine($"Content: {content}");
				System.Console.WriteLine(e.ToString());
				throw e;
			}
			catch (Exception e)
			{
				System.Console.WriteLine($"uri: {uri}");
				System.Console.WriteLine(e.ToString());
				throw e;
			}

			return result;
		}

		public static double EuklidianDistance(PointD p1, PointD p2)
		{
			return Math.Sqrt((p1.X - p2.X)*(p1.X - p2.X) + (p1.Y - p2.Y)*(p1.Y - p2.Y));
		}
		public static async Task<double> RouteDistance(Warehouse wh, int routeIndex, Func<PointD, PointD, Task<double>> fitness)
		{
			if (routeIndex < 0 || routeIndex >= wh.CarsAmount)
				throw new IndexOutOfRangeException();

			double result = 0;
			if (wh.CarRoutes[routeIndex].Count > 0)
			{
				List<Task<double>> resultsTasks = new List<Task<double>>(wh.CarRoutes[routeIndex].Count);
				resultsTasks.Add( fitness(wh.Point, wh.CarRoutes[routeIndex][0]) );
				for (int i = 1; i < wh.CarRoutes[routeIndex].Count; i++)
				{
					resultsTasks.Add( fitness(wh.CarRoutes[routeIndex][i-1], wh.CarRoutes[routeIndex][i]) );
				}
				resultsTasks.Add( fitness(wh.CarRoutes[routeIndex][wh.CarRoutes[routeIndex].Count - 1], wh.Point) );

				double[] results = await Task.WhenAll(resultsTasks);
				result = results.Sum();
			}
			return result;
		}
		public static double MapDistance(PointD p1, PointD p2, Mode mode)
		{

			if (Evaluation.EvalMode == EvaluationMode.Local)
			{
				return MapLocal(p1, p2, mode);
			}
			else
			{
				return MapFromServer(p1, p2, mode);
			}
		}
		private static double MapFromServer(PointD p1, PointD p2, Mode mode)
		{
			string uri = null;
			string argument = null;
			if (mode == Mode.Distance)
			{
				uri = $"/shortest/{p1};{p2}";
				argument = "meters_distance";
			}
			if ( mode == Mode.Time )
			{
				uri = $"/traveltime/{p1};{p2}";
				argument = "travel_time";
			}

			_semaphore.WaitOne();
			double result = Request(uri, argument);
			_semaphore.Release();

			return result;
		}
		private static double MapLocal(PointD p1, PointD p2, Mode mode)
		{
			return MapGraph.AStar(p1, p2, mode == Mode.Distance ? "length" : "travel_time");
		}
	}
}
