using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console
{
	public class Warehouse
	{
		private static Random rand = new Random();
		public static Func<PointD, PointD, Task<double>> fitness = Evaluation.MapDistance;//Evaluation.EuklidianDistance;

		public PointD Point;
		public readonly int CarsAmount;
		public readonly List<PointD>[] CarRoutes;
		public double Fitness { get; set; }
		public Warehouse(double lat, double lon, int cars)
		{
			Point = new PointD(lat, lon);
			CarsAmount	= cars;
			CarRoutes	= new List<PointD>[cars];
			for (int i = 0; i < CarRoutes.Length; i++)
			{
				CarRoutes[i] = new List<PointD>();
			}
		}
		public static Warehouse Random(PointD lower_left, PointD higher_right, int cars)
		{
			return new Warehouse(
				lower_left.X + rand.NextDouble()*(higher_right.X - lower_left.X),
				lower_left.Y + rand.NextDouble()*(higher_right.Y - lower_left.Y),
				cars);
		}

		public Warehouse Clone()
		{
			var wh = new Warehouse(this.Point.X, this.Point.Y, this.CarsAmount);
			for (int i = 0; i < CarsAmount; i++)
			{
				wh.CarRoutes[i] = new List<PointD>(this.CarRoutes[i]);
			}
			wh.Fitness = this.Fitness;
			return wh;
		}

		internal void InsertToCar(int carIndex, PointD coord)
		{
			if (carIndex >= CarsAmount || carIndex < 0)
				throw new IndexOutOfRangeException();

			CarRoutes[carIndex].Add(coord);
		}

		async internal Task<double> ComputeDistanceAndSave()
		{
			double result = await ComputeDistance();
			Fitness = result;
			return result;
		}
		async internal Task<double> ComputeDistance()
		{
			IList<Task<double>> computation = new List<Task<double>>(CarsAmount);
			for (int i = 0; i < CarsAmount; i++)
			{
				computation.Add( Evaluation.RouteDistance(this, routeIndex: i, fitness) );
			}
			double[] values = await Task.WhenAll( computation );
			double max = values.Max();
			return max;
		}
	}
}
