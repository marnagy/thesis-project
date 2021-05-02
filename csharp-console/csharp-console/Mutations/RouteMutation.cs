using csharp_console.Services;
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
		public async static Task Swap(WarehousesChromosome whc)
		{
			var rand = RandomService.GetInstance();
			Warehouse wh = whc.warehouses[rand.Next(whc.warehouses.Length)];
			double oldTimeFitness = wh.TimeFitness;
			double oldDistanceFitness = wh.DistanceFitness;
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

			double newTimeFitness = await wh.ComputeDistanceAndSave(Mode.Time);
			double newDistanceFitness = oldDistanceFitness;
			//if (WarehousesChromosome.Mode == Mode.Distance)
			newDistanceFitness = await wh.ComputeDistanceAndSave(Mode.Distance);
			//whc.UpdateFitness();
			if ( WarehousesChromosome.Mode == Mode.Time && newTimeFitness <= oldTimeFitness ||
				WarehousesChromosome.Mode == Mode.Distance && newDistanceFitness <= oldDistanceFitness )
			{
				whc.UpdateFitness();
				//whc. Fitness = whc.Fitness.Value - oldFitness + newFitness;
				return;
			}
			else
			{
				// swap back and set old fitness
				temp = route[index1];
				route[index1] = route[index2];
				route[index2] = temp;
				wh.ReturnFitness(oldTimeFitness, Mode.Time);
				wh.ReturnFitness(oldDistanceFitness, Mode.Distance);
			}


			//await whc.ComputeFitness();
		}
	}
}
