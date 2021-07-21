using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Mail;
using System.Net.Http;
using System.Threading.Tasks;
using System.Drawing;
using System.Text;
using System.Linq;
using System.Security;
using System.Diagnostics;
using Newtonsoft.Json;
using System.Threading;
using csharp_console.Services;

namespace csharp_console
{
	public class Program
	{
		static Func<int, string> csvTimeFile = (i) => $"result_{i}_time.csv";
		static Func<int, string> csvDistanceFile = (i) => $"result_{i}_distance.csv";
		static Func<int,string> outFile = (i) => $"result_{i}.wh";
		public static void Main(string[] args)
		{
			const string defaultLineSeparator = ";";
			const Mode defaultMode = Mode.Time;
			Config config;

			string lineSeparator = defaultLineSeparator;
			string source = string.Empty;
			string OutDir = string.Empty;
			Mode mode = defaultMode;
			string configFile = string.Empty;

			if (args.Length < 3)
			{
				Console.WriteLine($"You need to give at least 3 arguments:");
				Console.WriteLine("source file, output directory, configuration file, seed [int] (optional), mode [1=Time(default),2=Distance] (optional), use cache [0=no cache, 1=use cache(default)]");
				return;
			}

			{
				// set source file
				source = args[0];
				// file check
				if ( !File.Exists(source) )
				{
					Console.WriteLine("Source file does not exist");
					return;
				}
				Console.WriteLine($"Set source file to {source}");
			}

			{
				// set output directory
				OutDir = args[1];
				Console.WriteLine($"Set output directory file to {OutDir}");
				// if doesn't exist, create directory
				if (!Directory.Exists(OutDir))
					Directory.CreateDirectory(OutDir);
			}

			{
				// set config file
				configFile = args[2];
				// file check
				try
				{
					// load evolutionary algorithm constants
					config = Config.FromJson(configFile);
				}
				catch (FileNotFoundException)
				{
					Console.WriteLine("Config file does not exist");
					return;
				}
				Console.WriteLine($"Set config file to {configFile}");
				
				CheckConfiguration(config);
				Evaluation.StartManaging(locks: config.MaxParallelRequests);
				ThreadPool.SetMaxThreads(config.MaxParallelRequests, config.MaxParallelRequests);
				Evaluation.baseAddress = $"http://{config.ServerHost}:{config.ServerPort}";
				Evaluation.client.BaseAddress = new Uri( Evaluation.baseAddress );
				using ( var writer = new StreamWriter( File.OpenWrite(Path.Combine(OutDir, "config.json"))) )
				{
					writer.Write( config.ToString() );
				}
			}

			{
				// set seed
				if ( args.Length >= 4 )
				{
					if ( int.TryParse(args[3], out int seed) )
					{
						RandomService.SetSeed(seed);
						Console.WriteLine($"Seed set to {seed}.");
					}
					else
					{
						Console.WriteLine("Seed is not valid integer.");
						return;
					}
				}
			}

			{
				// set mode
				if (args.Length >= 5)
				{
					if ( int.TryParse(args[4], out int modeNum) && ( modeNum >= 1 && modeNum <= Enum.GetNames( typeof(Mode) ).Length ) )
					{
						mode = (Mode)modeNum;
						Console.WriteLine($"Mode set to {mode}.");
					}
					else
					{
						Console.WriteLine("Mode integer is not valid or does not fit given range.");
						return;
					}
				}
				// set mode in classes
				WarehousesChromosome.Mode = mode;
			}

			{
				// set mode
				if (args.Length >= 6)
				{
					if ( int.TryParse(args[5], out int cacheNum) )
					{
						if (cacheNum == 0)
						{
							Warehouse.SetCache(false);
						}
						Console.WriteLine("UseCache set to 'false'");
					}
					else
						Console.WriteLine("UseCache set to 'true'");
				}
				// set mode in classes
				WarehousesChromosome.Mode = mode;
			}

			// loading data from file
			IList<PointD> coords = new List<PointD>();
			string[] lineParts;

			foreach (var line in File.ReadLines(source))
			{
				lineParts = line.Split(lineSeparator);
				coords.Add( new PointD(
					double.Parse(lineParts[0].Replace('.', ',')), 
					double.Parse(lineParts[1].Replace('.', ','))
					) );
			}
			if (coords.Count == 0)
			{
				Console.WriteLine("No coordinates found.");
				return;
			}

			// set corner values
			PointD lowerLeft = new PointD(
					coords.Select(x => x.X).Min(),
					coords.Select(x => x.Y).Min()),
				higherRight = new PointD(
					coords.Select(x => x.X).Max(),
					coords.Select(x => x.Y).Max());

			// evolutionary algorithm
			IList<WarehousesChromosome> lastPopulation;
			WarehousesChromosome bestSolution;

			for (int i = 0; i < config.Runs; i++)
			{
				lastPopulation = GeneticAlgorithm(
						coords,
						lowerLeft,
						higherRight,
						config.PopulationSize,
						config.NGen,
						config.WarehouseMutProb,
						config.PointWarehouseMutProb,
						config.RouteMutProb,
						config.WarehousesAmount,
						config.CarsAmount,
						currentRun: i,
						OutputDirPath: OutDir
						);

				bestSolution = lastPopulation
					.First(	whch => whch.Fitness == lastPopulation.Min(whc => whc.Fitness) );

				string whText = bestSolution.ToString();

				string outFilePath = Path.Combine(OutDir, outFile(i));
				File.WriteAllText(outFilePath, whText);

				Console.WriteLine($"Program created file {outFilePath}\n");

			}
		}

		private static void CheckConfiguration(Config config)
		{
			if ( !(config.RouteMutProb >= 0 && config.RouteMutProb <= 1) )
			{
				Console.WriteLine("Illegal RouteMutProb. Needs to be in interval [0,1]. Please check config file.", Console.Error);
				System.Environment.Exit(0);
			}
			else if ( !(config.WarehouseMutProb >= 0 && config.WarehouseMutProb <= 1) )
			{
				Console.WriteLine("Illegal WarehouseMutProb. Needs to be in interval [0,1]. Please check config file.", Console.Error);
				System.Environment.Exit(0);
			}
			else if ( !(config.PointWarehouseMutProb >= 0 && config.PointWarehouseMutProb <= 1) )
			{
				Console.WriteLine("Illegal PointWarehouseMutProb. Needs to be in interval [0,1]. Please check config file.", Console.Error);
				System.Environment.Exit(0);
			}
			else if ( ! (config.WarehousesAmount == config.CarsAmount.Length) )
			{
				Console.WriteLine("WarehousesAmount does NOT match length of CarsAmount. Please check config file.", Console.Error);
				System.Environment.Exit(0);
			}
			else if ( !( config.CarsAmount.Length == config.CarsAmount.Where(c => c > 0).Count() ) )
			{
				Console.WriteLine("There is not reason for a warehouse to have less than 1 car. Please check config file.", Console.Error);
				System.Environment.Exit(0);
			}
		}

		static IList<WarehousesChromosome> InitPopulation(PointD lower_left, PointD higher_right,
			int amount, int warehouses_amount, int[] cars_amount, ISet<PointD> coords)
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
		
		static IList<WarehousesChromosome> GeneticAlgorithm(
			IList<PointD> coordsList, PointD lowerLeft, PointD higherRight, int populationAmount, int maxGenerations, 
			double warehouseMutProb, double pointWarehouseMutProb, double routeMutProb, int warehousesAmount, int[] carsAmount,
			int currentRun, string OutputDirPath)
		{
			ISet<PointD> coords = new HashSet<PointD>(coordsList);

			string csvTimePath = Path.Combine(OutputDirPath, csvTimeFile(currentRun) );
			string csvDistancePath = Path.Combine(OutputDirPath, csvDistanceFile(currentRun) );

			using ( StreamWriter csvTimeStream = new StreamWriter( File.Create( csvTimePath ) ),
								 csvDistanceStream = new StreamWriter( File.Create( csvDistancePath ) ) )
			{
				csvTimeStream.WriteLine("gen;std;min;avg;max");
				csvDistanceStream.WriteLine("gen;std;min;avg;max");
				Action<int, IList<WarehousesChromosome>> AddLog = (int gen, IList<WarehousesChromosome> whs) =>
				{
					Log(csvTimeStream, gen, whs, Mode.Time);
					Log(csvDistanceStream, gen, whs, Mode.Distance);
				};

				IList<WarehousesChromosome> lastPopulation = RunGA(
					lowerLeft, higherRight,
					populationAmount,
					warehousesAmount, carsAmount, coords,
					maxGenerations,
					AddLog,
					fitness: x => x.ComputeFitness(),
					warehouseMutation: Mutations.WarehouseMutation.NormalMove, warehouseMutProb,
					pointWarehouseMutation: Mutations.ChangeWarehouseOfPoint.SimpleChange, pointWarehouseMutProb,
					routeMutation: Mutations.RouteMutation.Swap, routeMutProb
					);

				return lastPopulation;
			}
		}
		private static void Log(StreamWriter writer, int gen, IList<WarehousesChromosome> population, Mode mode)
		{
			double[] values;
			switch (mode)
			{
				case Mode.Time:
					values = population.Select(x => x.TimeFitness).ToArray();
					break;
				case Mode.Distance:
					values = population.Select(x => x.DistanceFitness).ToArray();
					break;
				default:
					throw new Exception($"Unknown mode: {mode} found.");
			}

			// write to file
			double min = values.Min();
			double max = values.Max();
			double average = values.Average();
			double std = Statistics.StandardDeviation(values);

			Log log = new()
			{
				gen = gen,
				std = std,
				min = min,
				avg = average,
				max = max
			};
			writer.WriteLine(log);

			if (gen % 5 == 0)
						Console.WriteLine($"{mode}:\tgen: {gen}:\tstd: {Math.Round(std, 2)}\tmin: {Math.Round(min, 2)}\tavg: {Math.Round(average, 2)}\tmax: {Math.Round(max, 2)}");
		}
		static IList<WarehousesChromosome> RunGA(
			PointD lowerLeft, PointD higherRight,
			int populationAmount,
			int warehousesAmount, int[] carsAmount, ISet<PointD> coords,
			int maxGenerations,
			Action<int, IList<WarehousesChromosome>> addLog,
			Func<WarehousesChromosome, Task> fitness,
			Func<WarehousesChromosome, Task> warehouseMutation, double warehouseMutProb,
			Func<WarehousesChromosome, Task> pointWarehouseMutation, double pointWarehouseMutProb,
			Func<WarehousesChromosome, Task> routeMutation, double routeMutProb)
		{
			var population = InitPopulation(
				lowerLeft, higherRight, populationAmount,
				warehousesAmount, carsAmount, coords);

			// compute fitness
			Compute(population, fitness);

			for (int gen = 0; gen < maxGenerations; gen++)
			{

				addLog(gen, population);

				// mutation of position of warehouses
				Compute(population, warehouseMutation, warehouseMutProb);

				// mutation of point to warehouse mapping
				Compute(population, pointWarehouseMutation, pointWarehouseMutProb);

				// mutation of routes
				Compute(population, routeMutation, routeMutProb);
			}
			addLog(maxGenerations, population);
			return population;
		}
		private static void Compute(IList<WarehousesChromosome> population, Func<WarehousesChromosome, Task> func)
		{
			Compute(population, func, probability: 1.0d);
		}
		private static void Compute(IList<WarehousesChromosome> population, Func<WarehousesChromosome, Task> func, double probability)
		{
			bool[] flags = population
				.Select(_ => RandomService.NextDouble() < probability )
				.ToArray();
			int parThreads = flags.Where(f => f).Count();
			using (CountdownEvent evt = new CountdownEvent( parThreads ))
			{
				for (int index = 0; index < population.Count; index++)
				{
					if ( flags[index] )
					{
						int i = index;
						ThreadPool.QueueUserWorkItem( async _ => 
						{
							await func(population[i]);
							evt.Signal();
						});
					}
				}
				evt.Wait();
			}
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
