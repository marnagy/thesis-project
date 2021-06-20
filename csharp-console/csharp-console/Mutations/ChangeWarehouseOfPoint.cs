using csharp_console.Services;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console.Mutations
{
	class ChangeWarehouseOfPoint
	{
		public async static Task SimpleChange(WarehousesChromosome whc)
		{
			if (whc.warehouses.Length == 1 && whc.warehouses[0].CarRoutes.Length == 1) return;

			double oldTimeFitness = whc.TimeFitness;
			double oldDistanceFitness = whc.DistanceFitness;

			List<int> nonEmptyWHIndices = new List<int>();
			for (int i = 0; i < whc.warehouses.Length; i++)
			{
				var wh = whc.warehouses[i];
				if ( wh.CarRoutes.Any(route => route.Count > 0))
				{
					nonEmptyWHIndices.Add(i);
				}
			}

			int fromWHIndex = RandomService.Next(nonEmptyWHIndices.Count);
			Warehouse whFrom = whc.warehouses[nonEmptyWHIndices[fromWHIndex]];
			Warehouse whTo;
			double fromOldTimeFitness;
			double fromOldDistanceFitness;
			double toOldTimeFitness;
			double toOldDistanceFitness;
			int routeIndexFrom;
			int routeIndexTo;
			do
			{
				// allow adding to warehouses with all empty routes
				whTo = whc.warehouses[ RandomService.Next( whc.warehouses.Length ) ];

				fromOldTimeFitness = whFrom.TimeFitness;
				fromOldDistanceFitness = whFrom.DistanceFitness;
				toOldTimeFitness = whTo.TimeFitness;
				toOldDistanceFitness = whTo.DistanceFitness;

				routeIndexFrom = GetRouteIndexFrom(whFrom);
				routeIndexTo = GetRouteIndexTo(whTo);				
			} while (whFrom == whTo && routeIndexFrom == routeIndexTo);

			int pointIndexFrom = RandomService.Next(whFrom.CarRoutes[routeIndexFrom].Count);
			int pointIndexTo = RandomService.Next(whTo.CarRoutes[routeIndexTo].Count + 1);

			{
				PointD point = whFrom.CarRoutes[routeIndexFrom][pointIndexFrom];
				whFrom.CarRoutes[routeIndexFrom].RemoveAt(pointIndexFrom);
				whTo.CarRoutes[routeIndexTo].Insert(pointIndexTo, point);
			}

			double fromNewTimeFitness = await whFrom.ComputeDistanceAndSave(Mode.Time);
			double toNewTimeFitness = await whTo.ComputeDistanceAndSave(Mode.Time);

			double fromNewDistanceFitness = await whFrom.ComputeDistanceAndSave(Mode.Distance);
			double toNewDistanceFitness = await whTo.ComputeDistanceAndSave(Mode.Distance);

			if ( WarehousesChromosome.Mode == Mode.Time && Max(fromNewTimeFitness, toNewTimeFitness) < Max(fromOldTimeFitness, toOldTimeFitness) ||
				WarehousesChromosome.Mode == Mode.Distance && fromNewDistanceFitness + toNewDistanceFitness < fromOldDistanceFitness + toOldDistanceFitness )
			{
				whc.UpdateFitness();
				return;
			}
			else
			{
				// change back
				PointD point = whTo.CarRoutes[routeIndexTo][pointIndexTo];
				whTo.CarRoutes[routeIndexTo].RemoveAt(pointIndexTo);
				whFrom.CarRoutes[routeIndexFrom].Insert(pointIndexFrom, point);

				whTo.ReturnFitness(toOldTimeFitness, Mode.Time);
				whTo.ReturnFitness(toOldDistanceFitness, Mode.Distance);
				whFrom.ReturnFitness(fromOldTimeFitness, Mode.Time);
				whFrom.ReturnFitness(fromOldDistanceFitness, Mode.Distance);
			}
		}
		private static double Max(double d1, double d2)
		{
			if (d1 > d2)
				return d1;
			else
				return d2;
		}

		private static int GetRouteIndexTo(Warehouse whTo)
		{
			// maybe prefer routes with closer points?
			// random for now
			return RandomService.Next(whTo.CarRoutes.Length);
		}

		private static int GetRouteIndexFrom(Warehouse whFrom)
		{
			List<int> indices = new List<int>();
			for (int i = 0; i < whFrom.CarRoutes.Length; i++)
			{
				if (whFrom.CarRoutes[i].Count > 0)
					indices.Add(i);
			}
			return indices[RandomService.Next(indices.Count)];
		}
	}
}
