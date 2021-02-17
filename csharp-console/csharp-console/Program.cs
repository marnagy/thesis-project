using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Threading.Tasks;
using System.Drawing;
using System.Text;
using System.Linq;

namespace csharp_console
{
	public class Program
	{
		public static readonly Random rand = new Random();
		async static Task Main(string[] args)
		{
			const string defaultSource = "C:\\Users\\mnagy\\Documents\\Matfyz\\Semestral_project\\Semestral-project\\gps_coords.txt";
			const string defaultOutDir = "C:\\Users\\mnagy\\Documents\\Matfyz\\Semestral_project\\Semestral-project\\csharp_results";
			const string defaultOutFile = "result.txt";
			const char defaultLineSeparator = ';';

			string lineSeparator = defaultLineSeparator.ToString();
			string source = defaultSource;

			if (args.Length >= 1)
			{
				if ( int.TryParse( args[0], out int result) )
				{
					if (result >= 1 && result <= 2)
					{
						Warehouse.fitness = result == 1
							? Evaluation.EuklidianDistance
							: Evaluation.MapDistance;
					}
					else
					{
						throw new ArgumentException("Mode argument accepts integer values {1,2}");
					}
				}
				else
				{
					throw new ArgumentException("Mode argument accepts integer values {1,2}");
				}
			}
			if (args.Length >= 2)
			{
				source = args[1];
			}
			if (args.Length == 3)
			{
				lineSeparator = args[2];
			}

			// file check
			if ( !File.Exists(source) )
			{
				Console.WriteLine("Source file does not exist.");
				return;
			}

			// loading data from file
			IList<PointD> coords;
			using ( StreamReader sr = new StreamReader( new FileStream(source, FileMode.Open, FileAccess.Read) ) )
			{
				string line;
				string[] lineParts;
				coords = new List<PointD>();
				while ( (line = sr.ReadLine()) != null)
				{
					if ( int.TryParse(line, out var _))
					{
						continue;
					}
					lineParts = line.Split(lineSeparator);
					coords.Add( new PointD(double.Parse(lineParts[0].Replace('.', ',')), double.Parse(lineParts[1].Replace('.', ','))) );
				}
			}
			if (coords.Count == 0)
			{
				Console.WriteLine("No coordinates found.");
				return;
			}
				

			// get corners
			(double, double) lower_left_tup = (coords[0].X, coords[0].Y),
				higher_right_tup = (coords[0].X, coords[0].Y);
			foreach (var coord in coords)
			{
				if (coord.X < lower_left_tup.Item1)
				{
					lower_left_tup.Item1 = coord.X;
				}
				if (coord.X > higher_right_tup.Item1)
				{
					higher_right_tup.Item1 = coord.X;
				}

				if (coord.Y < lower_left_tup.Item2)
				{
					lower_left_tup.Item2 = coord.Y;
				}
				if (coord.Y > higher_right_tup.Item2)
				{
					higher_right_tup.Item2 = coord.Y;
				}
			}

			// set them in 
			PointD lowerLeft = new PointD(lower_left_tup.Item1, lower_left_tup.Item2),
				higherRight = new PointD(higher_right_tup.Item1, higher_right_tup.Item2);
			

			// Evolutionary algorithm constants
			int warehouses_amount = 1;
			int[] cars_amount = new[] {2};
			const int ngen = 20;
			const int amount = 10;
			const double cxProb = 0.2d;
			const double warehouseMutProb = 0.8d;
			const double routeMutProb = 0.8d;

			// evolutionary algorithm
			IList<(int, double, double, double)> logs = new List<(int, double, double, double)>();
			IList<WarehousesChromosome> population;
			WarehousesChromosome bestSolution;
			HttpClient client = new HttpClient();
			client.BaseAddress = new Uri("http://localhost:5000");
			(population, logs) = GeneticAlgorithm(
				coords,
				lowerLeft,
				higherRight,
				amount,
				ngen,
				cxProb,
				warehouseMutProb,
				routeMutProb,
				warehouses_amount,
				cars_amount,
				client
				);

			StringBuilder sb = new StringBuilder();
			bestSolution = population.First( whch => whch.Fitness.Value == population.Max(whc => whc.Fitness.Value));
			foreach (var warehouse in bestSolution.warehouses)
			{

				sb.AppendLine($"{warehouse.Point.X};{warehouse.Point.Y}");
				sb.AppendLine( warehouse.CarRoutes.Select(cr => cr.Count > 0 ? 1 : 0).Sum().ToString() );
				foreach (var cr in warehouse.CarRoutes)
				{
					if (cr.Count == 0) continue;

					for (int i = 0; i < cr.Count; i++)
					{
						sb.AppendLine($"{cr[i].X};{cr[i].Y}");
					}
					sb.AppendLine("---");
				}
				sb.AppendLine("###");
			}

			if (!Directory.Exists(defaultOutDir))
				Directory.CreateDirectory(defaultOutDir);
			string outFilePath = Path.Combine(defaultOutDir, defaultOutFile);
			File.WriteAllText(outFilePath, sb.ToString());

			Console.WriteLine($"Program created file {outFilePath}");
		}
		static IList<WarehousesChromosome> InitPopulation(PointD lower_left, PointD higher_right, int amount, int warehouses_amount, int[] cars_amount, ISet<PointD> coords)
		{
			WarehousesChromosome[] result = new WarehousesChromosome[amount];
			for (int i = 0; i < amount; i++)
			{
				var whc = new WarehousesChromosome(warehouses_amount, lower_left, higher_right, cars_amount);
				whc.InitRandomly(coords);
				result[i] = whc;
			}
			return result;
		}
		static (IList<WarehousesChromosome> lastPopulation,
			IList<(int, double, double, double)> logs) GeneticAlgorithm(
			IList<PointD> coordsList, PointD lowerLeft, PointD higherRight, int populationAmount, int maxGenerations, 
			double cxProb, double warehouseMutProb, double routeMutProb, int warehousesAmount, int[] carsAmount,
			HttpClient client)
		{
			ISet<PointD> coords = new HashSet<PointD>(coordsList);

			List<(int, double, double, double)> logs = new List<(int, double, double, double)>(maxGenerations);
			Action<int, IList<WarehousesChromosome>> AddLog = (int gen, IList<WarehousesChromosome> whs) =>
			{
				double min = whs[0].Fitness.HasValue ? whs[0].Fitness.Value : 0,
					max = whs[0].Fitness.HasValue ? whs[0].Fitness.Value : 100_000d,
					avg = 0;
				foreach (var wch in whs)
				{
					if (wch.Fitness.HasValue)
					{
						min = wch.Fitness.Value < min ? wch.Fitness.Value : min;
						max = wch.Fitness.Value > max ? wch.Fitness.Value : max;
						avg += wch.Fitness.Value;
					}
				}
				avg = avg / whs.Count;

				Console.WriteLine($"Generation {gen}:\tmin: {min}\tavg: {avg}\tmax: {max}");
				logs.Add( (gen, min, avg, max) );
			};

			// initialize population
			//IList<WarehousesChromosome> population = InitPopulation(
			//	lowerLeft, higherRight, populationAmount,
			//	warehouses_amount, cars_amount, coords);
			IList<WarehousesChromosome> lastPopulation;
			lastPopulation = RunGA(
				lowerLeft, higherRight, populationAmount,
				warehousesAmount, carsAmount, coords,
				maxGenerations,
				AddLog,
				fitness: x => x.ComputeFitness(  ),
				crossover: (p1, p2) => (p1, p2), cxProb,
				warehouseMutation: Mutations.WarehouseMutation.NormalMove, warehouseMutProb,
				routeMutation: Mutations.RouteMutation.Swap, routeMutProb,
				enviromentalCross: EnviromentalCrossover.MuCommaLambda
				);

			return (lastPopulation, logs);
		}
		static IList<WarehousesChromosome> RunGA(
			PointD lowerLeft, PointD higherRight, int populationAmount,
			int warehousesAmount, int[] carsAmount, ISet<PointD> coords,
			int maxGenerations,
			Action<int, IList<WarehousesChromosome>> addLog,
			Func<WarehousesChromosome, Task> fitness,
			Func<WarehousesChromosome, WarehousesChromosome, (WarehousesChromosome, WarehousesChromosome)> crossover, double cxProb,
			Func<WarehousesChromosome, Task> warehouseMutation, double warehouseMutProb,
			Func<WarehousesChromosome, Task> routeMutation, double routeMutProb,
			Func<IList<WarehousesChromosome>, IList<WarehousesChromosome>, IList<WarehousesChromosome>> enviromentalCross)
		{
			var population = InitPopulation(
				lowerLeft, higherRight, populationAmount,
				warehousesAmount, carsAmount, coords);

			ISet<Task> computation = new HashSet<Task>();
			for (int gen = 0; gen < maxGenerations; gen++)
			{
				computation.Clear();
				// compute fitness if neccessary
				foreach (var solution in population)
				{
					if (!solution.Fitness.HasValue)
						computation.Add( solution.ComputeFitness() );
				}
				Task.WhenAll(computation).Wait();

				addLog(gen, population);
				//WritePopulation(population);

				//List<(WarehousesChromosome, WarehousesChromosome)> parents = new List<(WarehousesChromosome, WarehousesChromosome)>(populationAmount*2);
				//for (int i = 0; i < populationAmount; i++)
				//{
				//	parents.Add( Selection.Tournament(population) );
				//}

				// mutation of position of warehouses
				computation.Clear();
				foreach (var solution in population)
				{
					if (rand.NextDouble() < warehouseMutProb)
						computation.Add(warehouseMutation(solution));
				}
				Task.WhenAll(computation).Wait();

				// mutation of routes
				computation.Clear();
				foreach (var solution in population)
				{
					if (rand.NextDouble() < routeMutProb)
						computation.Add(routeMutation(solution));
				}
				Task.WhenAll(computation).Wait();
			}
			addLog(maxGenerations, population);
			return population;
		}
		public static void WritePopulation(IList<WarehousesChromosome> population)
		{
			for (int i = 0; i < population.Count; i++)
			{
				Console.WriteLine($"Solution {i}");
				WarehousesChromosome solution = population[i];

				for (int j = 0; j < solution.warehouses.Length; j++)
				{
					Console.WriteLine($"\tWarehouse {j}");
					Warehouse wh = solution.warehouses[j];

					Console.WriteLine($"\tWarehouse point: lat: {wh.Point.X}, lon:{wh.Point.Y}");
					for (int k = 0; k < wh.CarsAmount; k++)
					{
						Console.WriteLine($"\t\tRoute {k}:");

					}

				}
				Console.WriteLine($"Sum of distances: {solution.Fitness}");

				Console.WriteLine();
				Console.WriteLine();
			}
		}
	}
}
