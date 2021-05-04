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
			List<PointD> route = wh.CarRoutes[ rand.Next(wh.CarsAmount) ];
			int length = route.Count;

			// this mutation has no sense if the route has less than 2 points
			if (length < 2)
				return;
			
			double oldTimeFitness = wh.TimeFitness;
			double oldDistanceFitness = wh.DistanceFitness;

			int index1 = rand.Next(length);
			int index2 = rand.Next(length);
			while (index1 == index2)
				index2 = rand.Next(length);

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
