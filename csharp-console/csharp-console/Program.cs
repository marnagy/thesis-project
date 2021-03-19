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

namespace csharp_console
{
	public class Program
	{
		public static readonly Random rand = new Random();
		async static Task Main(string[] args)
		{
			const string defaultSource = "C:\\Users\\mnagy\\Documents\\Matfyz\\Semestral_project\\Semestral-project\\python\\gps_coords.txt";
			const string defaultOutDir = "C:\\Users\\mnagy\\Documents\\Matfyz\\Semestral_project\\Semestral-project\\csharp_results";
			Func<int,string> outFile = (i) => $"result_{i}.wh";
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

			// get email address and password
			//MailAddress emailAddress;
			//SecureString password;
			//(emailAddress, password) = GetEmailCredentials();

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
			const int ngen = 30;
			const int amount = 8;
			const double cxProb = 0.2d;
			const double warehouseMutProb = 0.8d;
			const double pointWarehouseMutProb = 0.4d;
			const double routeMutProb = 0.8d;

			const int runsAmount = 10;

			// evolutionary algorithm
			IList<(int, double, double, double)> logs; // = new List<(int, double, double, double)>();
			IList<WarehousesChromosome> population;
			WarehousesChromosome bestSolution;
			StringBuilder sb;
			HttpClient client = new HttpClient();
			client.BaseAddress = new Uri("http://localhost:5000");

			//IList<(IList<WarehousesChromosome>, IList<(int, double, double, double)>)> results =
			//	new List<(IList<WarehousesChromosome> lastPopulation, IList<(int, double, double, double)>)>(n);
			for (int i = 0; i < runsAmount; i++)
			{
				//results.Add(
				(population, logs) = await GeneticAlgorithm(
						coords,
						lowerLeft,
						higherRight,
						amount,
						ngen,
						cxProb,
						warehouseMutProb,
						pointWarehouseMutProb,
						routeMutProb,
						warehouses_amount,
						cars_amount,
						client
						);

				bestSolution = population
					.First( 
						whch => whch.Fitness == population
							.Max(whc => whc.Fitness)
							);

				sb = new StringBuilder();
				sb.AppendLine(bestSolution.Fitness.ToString());
				foreach (var warehouse in bestSolution.warehouses)
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

				if (!Directory.Exists(defaultOutDir))
					Directory.CreateDirectory(defaultOutDir);
				string outFilePath = Path.Combine(defaultOutDir, outFile(i));
				File.WriteAllText(outFilePath, sb.ToString());

				Console.WriteLine($"Program created file {outFilePath}\n");

			}

			//SendEmail(emailAddress, password);
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
			double cxProb, double warehouseMutProb, double pointWarehouseMutProb, double routeMutProb, int warehousesAmount, int[] carsAmount,
			HttpClient client)
		{
			ISet<PointD> coords = new HashSet<PointD>(coordsList);

			List<(int, double, double, double)> logs = new List<(int, double, double, double)>(maxGenerations);
			Action<int, IList<WarehousesChromosome>> AddLog = (int gen, IList<WarehousesChromosome> whs) =>
			{
				double min = whs[0].Fitness,
					max = whs[0].Fitness,
					avg = 0;
				foreach (var wch in whs)
				{
					min = wch.Fitness < min ? wch.Fitness : min;
					max = wch.Fitness > max ? wch.Fitness : max;
					avg += wch.Fitness;
				}
				avg = avg / whs.Count;

				Console.WriteLine($"Generation {gen}:\tmin: {Math.Round(min, 3)}\tavg: {Math.Round(avg, 3)}\tmax: {Math.Round(max, 3)}");
				logs.Add( (gen, min, avg, max) );
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
				fitness: x => x.ComputeFitness(  ),
				crossover: (p1, p2) => (p1, p2), cxProb,
				warehouseMutation: Mutations.WarehouseMutation.NormalMove, warehouseMutProb,
				pointWarehouseMutation: Mutations.ChangeWarehouseOfPoint.SimpleChange, pointWarehouseMutProb,
				routeMutation: Mutations.RouteMutation.Swap, routeMutProb,
				enviromentalCross: EnviromentalCrossover.MuCommaLambda
				);

			return (lastPopulation, logs);
		}
		static async Task<IList<WarehousesChromosome>> RunGA(
			PointD lowerLeft, PointD higherRight, int populationAmount,
			int warehousesAmount, int[] carsAmount, ISet<PointD> coords,
			int maxGenerations,
			Action<int, IList<WarehousesChromosome>> addLog,
			Func<WarehousesChromosome, Task> fitness,
			Func<WarehousesChromosome, WarehousesChromosome, (WarehousesChromosome, WarehousesChromosome)> crossover, double cxProb,
			Func<WarehousesChromosome, Task> warehouseMutation, double warehouseMutProb,
			Func<WarehousesChromosome, Task> pointWarehouseMutation, double pointWarehouseMutProb,
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
					if (solution.Fitness < 0)
						computation.Add( solution.ComputeFitness() );
				}
				await Task.WhenAll(computation);

				addLog(gen, population);
				//WritePopulation(population);

				//List<(WarehousesChromosome, WarehousesChromosome)> parents = new List<(WarehousesChromosome, WarehousesChromosome)>(populationAmount*2);
				//for (int i = 0; i < populationAmount; i++)
				//{
				//	parents.Add( Selection.Tournament(population) );
				//}

				//var populationCopy = population.Select(whc => whc.Clone()).ToArray();

				// mutation of position of warehouses
				computation.Clear();
				foreach (var solution in population)
				{
					if (rand.NextDouble() < warehouseMutProb)
						computation.Add(warehouseMutation(solution));
				}
				await Task.WhenAll(computation);

				// mutation of position of warehouses
				computation.Clear();
				foreach (var solution in population)
				{
					if (rand.NextDouble() < warehouseMutProb)
						computation.Add(warehouseMutation(solution));
				}
				await Task.WhenAll(computation);

				// mutation of routes
				computation.Clear();
				foreach (var solution in population)
				{
					if (rand.NextDouble() < routeMutProb)
						computation.Add(routeMutation(solution));
				}
				await Task.WhenAll(computation);

				//IList<WarehousesChromosome> nextPopulation = new WarehousesChromosome[population.Count];
				//for (int i = 0; i < population.Count; i++)
				//{
				//	nextPopulation[i] = 
				//		population[i].Fitness <= populationCopy[i].Fitness
				//		? population[i]
				//		: populationCopy[i];
				//}
				//population = nextPopulation;
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
