using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console
{
	/// <summary>
	/// Class for statistics methods needed for logs.
	/// </summary>
	public static class Statistics
	{
		/// <summary>
		/// Standard deviation implementation.
		/// </summary>
		/// <param name="values"></param>
		/// <returns></returns>
		public static double StandardDeviation(IEnumerable<double> values)
		{
			double mean = values.Sum() / values.Count();
			double average = values.Average(); // for debugging

			double[] squares = values.Select(x => x*x).ToArray();
			double squaresSum = squares.Sum();

			double result = Math.Sqrt( squaresSum / (values.Count() - 1) );
			return result;
		}
	}
}
