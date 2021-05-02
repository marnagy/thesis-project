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

namespace csharp_console
{
	public class Evaluation
	{
		// public EventWaitHandle eventWaithandle = new ManualResetEvent(false);
		// public double result;
		public static readonly HttpClient client;
		public static string baseAddress { get; set; } = "http://localhost:5000";

		// optimalization if server cannot respond to all wanted requests
		//private static readonly ConcurrentQueue<(PointD, PointD, string)> msgs = new ConcurrentQueue<(PointD, PointD, string)>();
		//private static Queue<(PointD, PointD)> freeLocks;
		//private static object[] msgLocks;
		//private static bool[] msgIndicators;
		//private static int timeConst;
		private static Semaphore _pool;
		//private static bool killManager;
		//private static string requestUri;

		static Evaluation()
		{
			client = new HttpClient();
			client.BaseAddress = new Uri(baseAddress);
		}

		public static void StartManaging(int locks)
		{
			//ThreadPool.SetMaxThreads(locks, locks);
			_pool = new Semaphore(locks, locks*2);
			// msgLocks = new object[locks];
			// for (int i = 0; i < msgLocks.Length; i++)
			// {
			// 	msgLocks[i] = new object();
			// }
			//msgIndicators = new bool[locks];
			//timeConst = miliseconds;
		}

		private static double Request(string uri, string jsonArgument)
		{
			if (string.IsNullOrEmpty(uri)){
				throw new ArgumentException($"Wrong URI: {uri}");
			}
			// while ( true )
			// {
			// 	for (int i = 0; i < msgLocks.Length; i++)
			// 	{
			// 		//Console.WriteLine($"Trying lock number {i}");
			// 		if ( Monitor.TryEnter( msgLocks[i] ) )
			// 		{

			//Console.WriteLine($"Locked {i}");
			var req = new HttpRequestMessage(HttpMethod.Get, uri);
			//Console.WriteLine($"Sending request...");
			var temp1 = client.GetAsync(uri);
			temp1.Wait();
			var response = temp1.Result;
			//Console.WriteLine($"Received response...");
			var temp2 = response.Content.ReadAsStringAsync();
			temp2.Wait();
			var content = temp2.Result;
			double result;
			try{
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

			//Monitor.Exit( msgLocks[i] );
			return result;

			// 		}
			// 	}
			// 	//System.Console.WriteLine("Sleeping");
			// 	Thread.Sleep(timeConst);
			// }
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
				//result += await fitness(wh.Point, wh.CarRoutes[routeIndex][0]);
				resultsTasks.Add( fitness(wh.Point, wh.CarRoutes[routeIndex][0]) );
				for (int i = 1; i < wh.CarRoutes[routeIndex].Count; i++)
				{
					//result += await fitness(wh.CarRoutes[routeIndex][i-1], wh.CarRoutes[routeIndex][i]);
					resultsTasks.Add( fitness(wh.CarRoutes[routeIndex][i-1], wh.CarRoutes[routeIndex][i]) );
				}
				//result += await fitness(wh.CarRoutes[routeIndex][wh.CarRoutes[routeIndex].Count - 1], wh.Point);
				resultsTasks.Add( fitness(wh.CarRoutes[routeIndex][wh.CarRoutes[routeIndex].Count - 1], wh.Point) );

				double[] results = await Task.WhenAll(resultsTasks);
				result = results.Sum();
			}
			return result;
		}
		public static double MapDistance(PointD p1, PointD p2, Mode mode)
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

			//var msg = new HttpRequestMessage(HttpMethod.Get, uri);

			//bool success = false;
			//HttpResponseMessage response = null;

			// SEMAPHORE
			//System.Console.WriteLine("Waiting for semaphore...");
			_pool.WaitOne();
			//System.Console.WriteLine("In semaphore...");
			double result = Request(uri, argument);
			_pool.Release();
			//System.Console.WriteLine("Exited semaphore");
			//Console.WriteLine($"Got result {result}");


			// OTHER STUFF
			// var eval = new Evaluation();
			// ThreadPool.QueueUserWorkItem( _ =>
			// {
			// 	eval.result = Request(p1, p2, uri, argument);
			// 	eval.eventWaithandle.Set();
			// });
			// var thread = new Thread(new ThreadStart( () =>
			// {
			// 	result = Request(p1, p2, uri, argument);
			// 	eval.eventWaithandle.Set();
			// } ));
			// thread.Start();
			// await Task.Delay(2_000);
			// eval.eventWaithandle.WaitOne();
			// result = eval.result;
			//thread.Join();
			// var eval = new Evaluation();
			// ThreadPool.QueueUserWorkItem( evalObj =>
			// {
			// 	if ( evalObj != null )
			// 	{
			// 		var eval = (Evaluation)evalObj;
			// 		result = eval.Request(p1, p2, uri, jsonArgument: argument);
			// 		eval.eventWaithandle.Set();
			// 	}
			// }, eval, preferLocal: false);
			// eval.eventWaithandle.WaitOne();
			// ThreadPool.QueueUserWorkItem( objState => 
			// {
			// 	result = await Request(p1, p2, uri, jsonArgument: argument);
			// } );
			// var thread = new Thread(new ThreadStart( async () =>
			// {
			// 	result = await Request(p1, p2, uri, jsonArgument: argument);
			// } ));
			// thread.Start();
			// thread.Join();
			return result;
			//success = response.StatusCode == System.Net.HttpStatusCode.OK;
			//string content = await response.Content.ReadAsStringAsync();
			////try
			////{
			//var json = JsonConvert.DeserializeObject<Dictionary<string, double>>(content);
			//if (distance)
			//	return json["meters_distance"];
			//else
			//	return json["travel_time"];

			//}
			//catch (Exception e)
			//{
			//	int a = 5;
			//	return 100_000;
			//}
		}
	}
}
