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
		private WarehousesChromosome(Warehouse[] warehouses)
		{
			this.warehouses = new Warehouse[warehouses.Length];
			for (int i = 0; i < warehouses.Length; i++)
			{
				this.warehouses[i] = warehouses[i].Clone();
			}
		}
		public WarehousesChromosome(int length, PointD lower_left, PointD higher_right, int[] cars_amounts)
		{
			if (length <= 0 || cars_amounts.Length != length)
				throw new Exception("Wrong amount of warehouses or cars.");

			// create warehouses
			warehouses = new Warehouse[length];
			for (int i = 0; i < length; i++)
			{
				warehouses[i] = Warehouse.Random(lower_left, higher_right, cars_amounts[i]);
			}
		}
		public double Fitness { get => WarehousesChromosome.Mode == Mode.Time ? TimeFitness : DistanceFitness; }
		public double TimeFitness { get; set; }
		public double DistanceFitness { get; set; }

		public int Length { get; set; }

		// public WarehousesChromosome Clone()
		// {
		// 	var whc = new WarehousesChromosome(warehouses.Select(wh => wh.Clone()).ToArray());
		// 	whc.TimeFitness = this.TimeFitness;
		// 	whc.DistanceFitness = this.DistanceFitness;
		// 	return whc;
		// }

		public int CompareTo(WarehousesChromosome other)
		{
				return this.Fitness.CompareTo(other.Fitness);
		}

		//internal void ChangeWarehouseFitness(int index, double oldFitness, double newFitness)
		//{
		//	if (warehouses[index].Fitness.Value != oldFitness)
		//		throw new ArgumentException("Given wrong old fitness value.");

		//	warehouses[index].Fitness = newFitness;

		//	UpdateFitness();
		//}

		internal void InsertPoint(int warehouseIndex, int carIndex, PointD point)
		{
			if (warehouseIndex >= warehouses.Length || warehouseIndex < 0)
				throw new IndexOutOfRangeException();

			warehouses[warehouseIndex].InsertToCar(carIndex, point);
		}

		internal void InitRandomly(ISet<PointD> coords)
		{
			var rand = RandomService.GetInstance();
			foreach (var coord in coords)
			{
				var rand_value = rand.NextDouble();
				//var val = 1d / warehouses.Length;

				// calculate probabilities
				double[] distances = new double[warehouses.Length];
				for (int i = 0; i < warehouses.Length; i++)
				{
					var wh = warehouses[i];
					distances[i] = Evaluation.EuklidianDistance(coord, wh.Point);
				}
				var distancesSum = distances.Sum();
				var probabilities = distances.Select(x => x / distancesSum).ToArray();

				for (int i = 0; i < warehouses.Length; i++)
				{
					if (i < warehouses.Length - 1)
					{
						if (rand_value < probabilities[i])
						{
							warehouses[i].InsertToCar(rand.Next(warehouses[i].CarsAmount), coord);
							break;
						}
						else
						{
							rand_value -= probabilities[i];
						}
					}
					else
					{
						warehouses[i].InsertToCar(rand.Next(warehouses[i].CarsAmount), coord);
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
			//double[] values = 
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
        //async internal Task ComputeFitness()
        //{
        //	try{
        //		await ComputeFitness( Evaluation.EuklidianDistance );
        //	}
        //	catch (Exception e) {
        //		int a = 5;
        //	}
        //}
        public override string ToString()
        {
            var sb = new StringBuilder();
			sb.AppendLine(this.Fitness.ToString());
			foreach (var warehouse in this.warehouses)
			{

				sb.AppendLine($"{warehouse.Point.X};{warehouse.Point.Y}");
				//sb.AppendLine( warehouse.CarRoutes.Select(cr => cr.Count > 0 ? 1 : 0).Sum().ToString() );
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
