using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console.Services
{
	/// <summary>
	/// Thread-safe implementation of Random service
	/// </summary>
	public static class RandomService
	{
		private static Random rand;
		private static bool seedSet = false;

		static RandomService()
		{
			rand = new Random();
		}

		public static void SetSeed(int seed)
		{
			if ( !seedSet )
			{
				rand = new Random(seed);
				seedSet = true;
			}
		}
		public static int Next()
		{
			lock (rand)
			{
				return rand.Next();
			}
		}
		public static int Next(int maxValue)
		{
			lock (rand)
			{
				return rand.Next(maxValue);
			}
		}
		public static int Next(int minValue, int maxValue)
		{
			lock (rand)
			{
				return rand.Next(minValue, maxValue);
			}
		}
		public static double NextDouble()
		{
			lock (rand)
			{
				return rand.NextDouble();
			}
		}
		public static double NextGaussian(double mu = 0, double sigma = 1)
		{
			lock (rand)
			{
				return rand.NextGaussian(mu, sigma);
			}
		}
	}
}
