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
		public static Random GetInstance()
		{
			if (rand == null)
			{
				rand = new Random();
			}
			return rand;
		}
	}
}
