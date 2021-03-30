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

namespace csharp_console
{
	public class Program
	{
		public static readonly Random rand = new Random();
		static Func<int, string> logFile = (i) => $"result_{i}.log";
		static Func<int,string> outFile = (i) => $"result_{i}.wh";
		async static Task Main(string[] args)
		{
			string defaultSource = "C:\\Users\\mnagy\\Documents\\Matfyz\\Semestral_project\\Semestral-project\\gps_coords.txt";
			string defaultOutDir = "csharp_results";
			const string defaultLineSeparator = ";";

			string lineSeparator = defaultLineSeparator;
			string source = defaultSource;
			string OutDir = defaultOutDir;
			string configFile = "..\\..\\..\\..\\..\\config.json";

			if (args.Length < 3)
			{
				Console.WriteLine($"You need to give at least 3 arguments. [source file, output directory, configuration file]");
				return;
			}

			if (args.Length >= 1)
			{
				source = args[0];
				// file check
				if ( !File.Exists(source) )
				{
					Console.WriteLine("Source file does not exist");
					return;
				}
				Console.WriteLine($"Set source file to {source}");
			}
			if (args.Length >= 2)
			{
				OutDir = args[1];
				Console.WriteLine($"Set output directory file to {OutDir}");
			}
			if (args.Length >= 3)
			{
				configFile = args[2];
				// file check
				if ( !File.Exists(configFile) )
				{
					Console.WriteLine("Config file does not exist");
					return;
				}
				Console.WriteLine($"Set config file to {configFile}");
			}

			// if doesn't exist, create directory
			if (!Directory.Exists(OutDir))
				Directory.CreateDirectory(OutDir);

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

			// set corner values
			PointD lowerLeft = new PointD(
					coords.Select(x => x.X).Min(),
					coords.Select(x => x.Y).Min()),
				higherRight = new PointD(
					coords.Select(x => x.X).Max(),
					coords.Select(x => x.Y).Max());
			

			// load evolutionary algorithm constants
			var config = LoadConfig(configFile);
			// Debug.Assert( config.PopulationSize % 5 == 0 );
			// Debug.Assert( config.NGen % 5 == 0 );
			CheckConfiguration(config);

			// evolutionary algorithm
			IList<(int, double, double, double)> logs; // = new List<(int, double, double, double)>();
			IList<WarehousesChromosome> population;
			WarehousesChromosome bestSolution;

			for (int i = 0; i < config.Runs; i++)
			{
				//results.Add(
				(population, logs) = await GeneticAlgorithm(
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
						OutDir
						);

				bestSolution = population
					.First( 
						whch => whch.Fitness == population
							.Min(whc => whc.Fitness)
							);

				string whText = bestSolution.ToString();

				string outFilePath = Path.Combine(OutDir, outFile(i));
				File.WriteAllText(outFilePath, whText);

				Console.WriteLine($"Program created file {outFilePath}\n");

			}

			//SendEmail(emailAddress, password);
		}

		private static void CheckConfiguration(Config config)
		{
			//Console.WriteLine(config.ToString());
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

		private static Config LoadConfig(string configFile)
		{
			string text = File.ReadAllText(configFile);
			var config = JsonConvert.DeserializeObject<Config>(text);
			return config;
		}

		private static (MailAddress emailAddress, SecureString password) GetEmailCredentials()
		{
			Console.Write("Your gmail address: ");
			MailAddress address = new MailAddress(Console.ReadLine());
			Console.Write("Your password: ");
			SecureString password = GetPassword();
			return (address, password);
		}

		private static SecureString GetPassword()
		{
			var res = new SecureString();
			ConsoleKeyInfo nextKey;

			while ( (nextKey = Console.ReadKey(true)).Key != ConsoleKey.Enter)
			{
				if ( nextKey.Key == ConsoleKey.Backspace)
				{
					if (res.Length > 0)
					{
						res.RemoveAt(res.Length - 1);
						// erase the last * as well
						Console.Write(nextKey.KeyChar);
						Console.Write(" ");
						Console.Write(nextKey.KeyChar);
					}
				}
				else
				{
					res.AppendChar(nextKey.KeyChar);
					Console.Write("*");
				}
			}
			Console.WriteLine();
			res.MakeReadOnly();
			return res;
		}

		private static void SendEmail(MailAddress address, SecureString password)
		{
			var smtp = new SmtpClient
			{
				Host = "smtp.gmail.com",
				Port = 587,
				EnableSsl = true,
				DeliveryMethod = SmtpDeliveryMethod.Network,
				UseDefaultCredentials = false,
				Credentials = new NetworkCredential(address.Address, password)
			};
			using (var message = new MailMessage(address, address)
			{
				Subject = "Program ended",
				Body = $"Your program has ended at {DateTime.Now}."
			})
			{
				smtp.Send(message);
			}
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
		
		static async Task<(IList<WarehousesChromosome> lastPopulation,
			IList<(int, double, double, double)> logs)> GeneticAlgorithm(
			IList<PointD> coordsList, PointD lowerLeft, PointD higherRight, int populationAmount, int maxGenerations, 
			double warehouseMutProb, double pointWarehouseMutProb, double routeMutProb, int warehousesAmount, int[] carsAmount,
			int currentRun, string OutputDirPath)
		{
			ISet<PointD> coords = new HashSet<PointD>(coordsList);

			List<(int, double, double, double)> logs = new List<(int, double, double, double)>(maxGenerations);

			var dt = DateTime.Now;
			string logOutPath = Path.Combine(OutputDirPath, logFile(currentRun) );
			using ( StreamWriter logOutStream = new StreamWriter( File.Create( logOutPath ) ) )
			{
				Action<int, IList<WarehousesChromosome>> AddLog = (int gen, IList<WarehousesChromosome> whs) =>
				{
					var values = whs.Select(x => x.Fitness).ToArray();
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
					logOutStream.WriteLine( JsonConvert.SerializeObject(log) );

					if (gen % 10 == 0)
						Console.WriteLine($"Generation {gen}:\tstd: {Math.Round(std, 3)}\tmin: {Math.Round(min, 3)}\tavg: {Math.Round(average, 3)}\tmax: {Math.Round(max, 3)}");

					logs.Add( (gen, min, average, max) );
				};

				// initialize population
				//IList<WarehousesChromosome> population = InitPopulation(
				//	lowerLeft, higherRight, populationAmount,
				//	warehouses_amount, cars_amount, coords);
				IList<WarehousesChromosome> lastPopulation;

				lastPopulation = await RunGA(
					lowerLeft, higherRight, populationAmount,
					warehousesAmount, carsAmount, coords,
					maxGenerations,
					AddLog,
					fitness: x => x.ComputeFitness(),
					warehouseMutation: Mutations.WarehouseMutation.NormalMove, warehouseMutProb,
					pointWarehouseMutation: Mutations.ChangeWarehouseOfPoint.SimpleChange, pointWarehouseMutProb,
					routeMutation: Mutations.RouteMutation.Swap, routeMutProb
					);

				return (lastPopulation, logs);
			}
		}
		static async Task<IList<WarehousesChromosome>> RunGA(
			PointD lowerLeft, PointD higherRight, int populationAmount,
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

			ISet<Task> computation = new HashSet<Task>();

			// compute fitness
			await Compute(population, fitness);

			for (int gen = 0; gen < maxGenerations; gen++)
			{

				//Console.WriteLine("Logging...");
				addLog(gen, population);

				// mutation of position of warehouses
				//Console.WriteLine("Warehouse mutation...");
				await Compute(population, warehouseMutation, warehouseMutProb);

				// mutation of position of warehouses
				//Console.WriteLine("Point warehouse mutation...");
				await Compute(population, pointWarehouseMutation, pointWarehouseMutProb);

				// mutation of routes
				//Console.WriteLine("Route mutation...");
				await Compute(population, routeMutation, routeMutProb);
			}
			addLog(maxGenerations, population);
			return population;
		}
		private static async Task Compute(IList<WarehousesChromosome> population, Func<WarehousesChromosome, Task> func)
		{
			await Compute(population, func, probability: 1.5);
		}
		private static async Task Compute(IList<WarehousesChromosome> population, Func<WarehousesChromosome, Task> func, double probability)
		{
			const int stepSize = 2;

			ISet<Task> computations = new HashSet<Task>(capacity: stepSize);
			for (int i = stepSize; i < population.Count + stepSize; i += stepSize)
			{
				computations.Clear();
				for (int j = 0; j < stepSize; j++)
				{
					int index = i - stepSize + j;
					if ( index < population.Count && rand.NextDouble() < probability )
						computations.Add( func(population[index]) );
				}
				await Task.WhenAll(computations);
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
