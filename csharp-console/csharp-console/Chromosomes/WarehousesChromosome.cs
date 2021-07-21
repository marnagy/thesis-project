using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;
using csharp_console.Services;

namespace csharp_console
{
	public class WarehousesChromosome : IComparable<WarehousesChromosome>
	{
		public static Mode Mode;

		// instance variables
		public readonly Warehouse[] warehouses;
		public WarehousesChromosome(int length, PointD lowerLeft, PointD higherRight, int[] carsAmounts)
		{
			if (length <= 0 || carsAmounts.Length != length)
				throw new Exception("Wrong amount of warehouses or cars.");

			// create warehouses
			warehouses = new Warehouse[length];
			for (int i = 0; i < length; i++)
			{
				warehouses[i] = Warehouse.Random(lowerLeft, higherRight, carsAmounts[i]);
			}
		}
		public double Fitness { get => WarehousesChromosome.Mode == Mode.Time ? TimeFitness : DistanceFitness; }
		public double TimeFitness { get; set; } = 0.0;
		public double DistanceFitness { get; set; } = 0.0;

		public int CompareTo(WarehousesChromosome other)
		{
				return this.Fitness.CompareTo(other.Fitness);
		}

		internal void InsertPoint(int warehouseIndex, int carIndex, PointD point)
		{
			if (warehouseIndex >= warehouses.Length || warehouseIndex < 0)
				throw new IndexOutOfRangeException();

			warehouses[warehouseIndex].InsertToCar(carIndex, point);
		}

		internal void InitRandomly(ISet<PointD> coords)
		{
			foreach (var coord in coords)
			{
				var rand_value = RandomService.NextDouble();

				// calculate probabilities
				double[] distances = new double[warehouses.Length];
				for (int i = 0; i < warehouses.Length; i++)
				{
					var wh = warehouses[i];
					distances[i] = Evaluation.EuklidianDistance(coord, wh.Point);
				}
				double[] probabilities = distances.Select(x => 1 / x).ToArray();
				double probSum = probabilities.Sum();
				for (int p = 0; p < probabilities.Length; p++)
				{
					probabilities[p] = probabilities[p] / probSum;
				}

				for (int i = 0; i < warehouses.Length; i++)
				{
					if (i < warehouses.Length - 1)
					{
						if (rand_value < probabilities[i])
						{
							warehouses[i].InsertToCar(RandomService.Next(warehouses[i].CarsAmount), coord);
							break;
						}
						else
						{
							rand_value -= probabilities[i];
						}
					}
					else
					{
						warehouses[i].InsertToCar(RandomService.Next(warehouses[i].CarsAmount), coord);
					}
				}
			}
		}

		async internal Task ComputeFitness()
		{
			List<Task<double>> warehouseTasks = new List<Task<double>>();
			foreach (var warehouse in warehouses)
			{
				warehouseTasks.Add( warehouse.ComputeDistanceAndSave(Mode.Time) );
				warehouseTasks.Add( warehouse.ComputeDistanceAndSave(Mode.Distance) );
			}
			await Task.WhenAll( warehouseTasks );

			UpdateFitness();
		}
		internal void UpdateFitness()
		{
			// Time part
			{
				var values = warehouses.Select(wh => wh.TimeFitness);
				TimeFitness = values.Max();
			}

			// Distance part
			{
				var values = warehouses.Select(wh => wh.DistanceFitness);
				DistanceFitness = values.Sum();
			}
		}
        public override string ToString()
        {
            var sb = new StringBuilder();
			sb.AppendLine(TimeFitness.ToString());
			sb.AppendLine(DistanceFitness.ToString());
			foreach (var warehouse in this.warehouses)
			{

				sb.AppendLine($"{warehouse.Point.X};{warehouse.Point.Y}");
				foreach (var cr in warehouse.CarRoutes)
				{
					if (cr.Count == 0) continue;

					for (int j = 0; j < cr.Count; j++)
					{
						if (j > 0)
							sb.Append(';');
						sb.Append($"{cr[j].X};{cr[j].Y}");
					}
					sb.AppendLine();
				}
				sb.AppendLine("###");
			}
			return sb.ToString();
        }
	}
}
