using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console
{
	public static class Selection
	{
		private static readonly Random rand = new Random();
		internal static (WarehousesChromosome, WarehousesChromosome) Tournament(IList<WarehousesChromosome> population)
		{
			int amount = 3;

			WarehousesChromosome p1 = population[rand.Next(population.Count)];
			for (int i = 0; i < amount; i++)
			{
				var temp = population[rand.Next(population.Count)];
				if (temp.Fitness > p1.Fitness)
					p1 = temp;
			}

			WarehousesChromosome p2 = population[rand.Next(population.Count)];
			for (int i = 0; i < amount; i++)
			{
				var temp = population[rand.Next(population.Count)];
				if (temp.Fitness > p2.Fitness)
					p2 = temp;
			}
			return (p1, p2);
		}
	}
}
