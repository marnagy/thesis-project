using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console.Services
{
	public static class RandomService
	{
		private static Random rand;
		public static void SetSeed(int seed)
		{
			rand = new Random(seed);
		}
		//public static Random GetInstance()
		//{
		//	if (rand == null)
		//	{
		//		rand = new Random();
		//	}
		//	return rand;
		//}
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
