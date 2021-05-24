using csharp_console.Services;
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
		//public static Func<PointD, PointD, Task<double>> fitness = async (p1, p2) => {
			
		//} ; //Evaluation.EuklidianDistance;

		public PointD Point;
		public readonly int CarsAmount;
		public readonly List<PointD>[] CarRoutes;
		public double Fitness { get => WarehousesChromosome.Mode == Mode.Time ? TimeFitness : DistanceFitness; }
		public double TimeFitness { get; set; }
		public double DistanceFitness { get; set; }
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
		public static void SetSeed(int seed)
		{
			rand = new Random(seed);
		}
		public Warehouse Clone()
		{
			var wh = new Warehouse(this.Point.X, this.Point.Y, this.CarsAmount);
			for (int i = 0; i < CarsAmount; i++)
			{
				wh.CarRoutes[i] = new List<PointD>(this.CarRoutes[i]);
			}
			wh.TimeFitness = this.TimeFitness;
			wh.DistanceFitness = this.DistanceFitness;
			return wh;
		}

		internal void ReturnFitness(double oldFitness, Mode mode)
		{
			if (mode == Mode.Time)
				TimeFitness = oldFitness;
			if (mode == Mode.Distance)
				DistanceFitness = oldFitness;
		}

		internal void InsertToCar(int carIndex, PointD coord)
		{
			if (carIndex >= CarsAmount || carIndex < 0)
				throw new IndexOutOfRangeException();

			CarRoutes[carIndex].Add(coord);
		}

		//async internal Task<double> ComputeDistanceAndSave()
		//{
		//	double timeResult = await ComputeFitness(Mode.Time);
		//	TimeFitness = timeResult;

		//	double distanceResult = await ComputeFitness(Mode.Distance);
		//	DistanceFitness = distanceResult;

		//	return Warehouse.Mode == Mode.Time ? TimeFitness : DistanceFitness;
		//}

		async internal Task<double> ComputeDistanceAndSave(Mode mode)
		{
			double result = await ComputeFitness(mode);
			if (mode == Mode.Time)
				TimeFitness = result;
			if (mode == Mode.Distance)
				DistanceFitness = result;
			return result;
		}
		async internal Task<double> ComputeFitness(Mode mode)
		{
			IList<Task<double>> computation = new List<Task<double>>(CarsAmount);
			for (int i = 0; i < CarsAmount; i++)
			{
				computation.Add(
					Evaluation.RouteDistance(this,
						routeIndex: i,
						fitness: (p1, p2) => FitnessFunc(p1, p2, mode)
					)
				);
			}
			double[] values = await Task.WhenAll( computation );
			double result = WarehousesChromosome.Mode == Mode.Time ? values.Max() : values.Sum();
			return result;
		}
		private async Task<double> FitnessFunc(PointD p1, PointD p2, Mode mode)
		{
			if ( DBService.TryGetFitness(p1, p2, mode, out double value) )
			{
				return await Task.FromResult(value);
			}
			else
			{
				var val = Evaluation.MapDistance(p1, p2, mode);
				DBService.TryAddValue(p1, p2, mode, val);
				return val;
			}
		}
		public override string ToString()
		{
			var sb = new StringBuilder(
			$"Warehouse point: {this.Point}\n" +
				"CarRoutes:");
			foreach (var route in CarRoutes)
			{
				if (route.Count == 0)
					continue;

				sb.Append('\n');
				foreach (var point in route)
				{
					sb.Append(point);
				}
			}
			return sb.ToString();
		}
	}
}
