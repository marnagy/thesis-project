using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console.Mutations
{
	public static class RouteMutation
	{
		private static readonly Random rand = new Random();
		public async static Task Swap(WarehousesChromosome whc)
		{
			Warehouse wh = whc.warehouses[rand.Next(whc.warehouses.Length)];
			double oldFitness = wh.Fitness.HasValue ? wh.Fitness.Value : 100_000d ;
			List<PointD> route = wh.CarRoutes[ rand.Next(wh.CarsAmount) ];
			int length = route.Count;
			if (length < 2)
				return;

			int index1 = rand.Next(length);
			var other = new List<int>(length-1);
			for (int i = 0; i < length; i++)
			{
				if (i != index1)
				{
					other.Add(i);
				}
			}
			int index2 = other[ rand.Next(length-1) ];

			PointD temp = route[index1];
			route[index1] = route[index2];
			route[index2] = temp;

			double newFitness = await wh.ComputeDistanceAndSave();
			if (newFitness < oldFitness)
			{
				whc.Fitness = whc.Fitness.Value - oldFitness + newFitness;
				return;
			}
			else
			{
				// swap back and set old fitness
				temp = route[index1];
				route[index1] = route[index2];
				route[index2] = temp;
				wh.Fitness = oldFitness;
			}


			//await whc.ComputeFitness();
		}
	}
}
