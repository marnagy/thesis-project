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
		private static readonly Random rand = new Random();
		private static double sigma = 0.005;
		//private static int succesfulUpdateCounter = 0;
		//private static int counter = 0;
		public async static Task NormalMove(WarehousesChromosome whc)
		{
			int whIndex = rand.Next(whc.warehouses.Length);
			Warehouse wh = whc.warehouses[whIndex];
			double oldFitness = wh.Fitness;
			PointD oldPoint = wh.Point;
			PointD newPoint;

			double x, y;
			x = rand.NextGaussian(oldPoint.X, sigma);
			y = rand.NextGaussian(oldPoint.Y, sigma);
			newPoint = new PointD(x, y);

			wh.Point = newPoint;

			double newFitness = await wh.ComputeDistanceAndSave();
			//whc.UpdateFitness();
			if (newFitness <= oldFitness)
			{
				whc.UpdateFitness();
			}
			else
			{
				// set old point and fitness back
				wh.Point = oldPoint;
				wh.Fitness = oldFitness;
			}
			//else
			//	succesfulUpdateCounter += 1;
			//counter += 1;
		}
	}
}
