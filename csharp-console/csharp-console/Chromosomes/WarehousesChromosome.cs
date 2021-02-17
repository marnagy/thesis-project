using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Http;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console
{
	public class WarehousesChromosome : IComparable<WarehousesChromosome>
	{
		// static variables
		private static readonly Random rand;
		private static readonly HttpClient Client;
		static WarehousesChromosome()
		{
			rand = new Random();
			Client = new HttpClient();
			Client.BaseAddress = new Uri("http://localhost:5000");
		}

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
		public double? Fitness { get; set; }

		public int Length { get; set; }

		public WarehousesChromosome Clone()
		{
			return new WarehousesChromosome(this.warehouses);
		}

		public int CompareTo(WarehousesChromosome other)
		{
			if (this.Fitness.HasValue && other.Fitness.HasValue)
			{
				return this.Fitness.Value.CompareTo(other.Fitness.Value);
			}
			else
				return this.Fitness.HasValue ? 1 : -1;
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
				var rand_value = rand.NextDouble();
				var val = 1d / warehouses.Length;
				for (int i = 0; i < warehouses.Length; i++)
				{
					if (i < warehouses.Length - 1)
					{
						if (rand_value < val)
						{
							warehouses[i].InsertToCar(rand.Next(warehouses[i].CarsAmount), coord);
							break;
						}
						else
						{
							rand_value -= val;
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
				warehouseTasks.Add( warehouse.ComputeDistanceAndSave() );
			}
			double[] values = await Task.WhenAll( warehouseTasks );

			Fitness = values.Max(); //.Sum();
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
	}
}
