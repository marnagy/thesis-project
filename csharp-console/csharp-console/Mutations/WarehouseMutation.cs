using csharp_console.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console.Mutations
{
	public static class WarehouseMutation
	{
		private static double sigma = 0.005;
		public async static Task NormalMove(WarehousesChromosome whc)
		{
			int whIndex = RandomService.Next(whc.warehouses.Length);
			Warehouse wh = whc.warehouses[whIndex];
			
			double oldTimeFitness = wh.TimeFitness;
			double oldDistanceFitness = wh.DistanceFitness;
			PointD oldPoint = wh.Point;
			PointD newPoint;

			double x, y;
			x = RandomService.NextGaussian(oldPoint.X, sigma);
			y = RandomService.NextGaussian(oldPoint.Y, sigma);
			if ( double.IsNaN(x) || double.IsNaN(y))
			{
				Console.WriteLine($"Old Points: {oldPoint.X}, {oldPoint.Y}");
				Console.WriteLine($"New Points: {x}, {y}");
			}
			newPoint = new PointD(x, y);

			wh.Point = newPoint;

			double newTimeFitness = await wh.ComputeDistanceAndSave(Mode.Time);
			double newDistanceFitness = await wh.ComputeDistanceAndSave(Mode.Distance);
			if ( WarehousesChromosome.Mode == Mode.Time    && newTimeFitness <= oldTimeFitness ||
				WarehousesChromosome.Mode == Mode.Distance && newDistanceFitness <= oldDistanceFitness )
			{
				whc.UpdateFitness();
			}
			else
			{
				// set old point and fitness back
				wh.Point = oldPoint;
				wh.ReturnFitness(oldTimeFitness, Mode.Time);
				wh.ReturnFitness(oldDistanceFitness, Mode.Distance);
			}
		}
	}
}
