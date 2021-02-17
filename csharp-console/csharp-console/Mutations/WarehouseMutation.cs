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
		const double updRateValue = 0.2;
		const double updConst = 1.2;

		private static readonly Random rand = new Random();
		private static double sigma = 1;
		//private static int succesfulUpdateCounter = 0;
		//private static int counter = 0;
		public async static Task NormalMove(WarehousesChromosome whc)
		{
			Warehouse wh = whc.warehouses[rand.Next(whc.warehouses.Length)];
			double oldFitness = wh.Fitness.HasValue ? wh.Fitness.Value : 100_000d ;
			PointD oldPoint = wh.Point;
			PointD newPoint;

			double x, y;
			x = RandomExtensions.NextGaussian(rand, oldPoint.X, sigma);
			y = RandomExtensions.NextGaussian(rand, oldPoint.Y, sigma);
			newPoint = new PointD(x, y);

			wh.Point = newPoint;

			double newFitness = await wh.ComputeDistanceAndSave();
			if (newFitness <= oldFitness)
			{
				// set old point and fitness back
				wh.Point = oldPoint;
				wh.Fitness = oldFitness;
			}
			//else
			//	succesfulUpdateCounter += 1;
			//counter += 1;
		}
		//public static void UpdateSigma()
		//{
		//	double value = (double)succesfulUpdateCounter / counter;
		//	if (value > updRateValue)
		//		sigma *= updConst;
		//	else
		//		sigma /= updConst;
		//}
	}
}
