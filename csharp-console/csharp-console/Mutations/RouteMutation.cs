﻿using csharp_console.Services;
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
			Warehouse wh = whc.warehouses[RandomService.Next(whc.warehouses.Length)];
			List<PointD> route = wh.CarRoutes[ RandomService.Next(wh.CarsAmount) ];
			int length = route.Count;

			// this mutation has no sense if the route has less than 2 points
			if (length < 2)
				return;
			
			double oldTimeFitness = wh.TimeFitness;
			double oldDistanceFitness = wh.DistanceFitness;

			int index1 = RandomService.Next(length);
			int[] availableIndices = new int[length-1];
			{
				int temp = 0;
				for (int i = 0; i < length; i++)
				{
					if (i == index1){
						temp = 1;
						continue;
					}
					
					availableIndices[i - temp] = i;
				}
			}
			int index2 = availableIndices[ RandomService.Next(availableIndices.Length) ];

			{
				PointD temp = route[index1];
				route[index1] = route[index2];
				route[index2] = temp;
			}

			double newTimeFitness = await wh.ComputeDistanceAndSave(Mode.Time);
			double newDistanceFitness = await wh.ComputeDistanceAndSave(Mode.Distance);
			if ( WarehousesChromosome.Mode == Mode.Time && newTimeFitness <= oldTimeFitness ||
				WarehousesChromosome.Mode == Mode.Distance && newDistanceFitness <= oldDistanceFitness )
			{
				whc.UpdateFitness();
			}
			else
			{
				// swap back and set old fitness
				{
					var temp = route[index1];
					route[index1] = route[index2];
					route[index2] = temp;
				}
				wh.ReturnFitness(oldTimeFitness, Mode.Time);
				wh.ReturnFitness(oldDistanceFitness, Mode.Distance);
			}
		}
	}
}
