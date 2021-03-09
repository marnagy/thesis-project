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
		public double Fitness { get; set; } = -1;

		public int Length { get; set; }

		public WarehousesChromosome Clone()
		{
			var whc = new WarehousesChromosome(warehouses.Select(wh => wh.Clone()).ToArray());
			whc.Fitness = this.Fitness;
			return whc;
		}

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
			//double[] values = 
			await Task.WhenAll( warehouseTasks );

			UpdateFitness();
		}
		internal void UpdateFitness()
		{
			double[] values = warehouses.Select(wh => wh.Fitness).ToArray();
			Fitness = values.Max();
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
