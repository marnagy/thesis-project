using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console
{
	public struct PointD
	{
		public readonly double X, Y;
		public PointD(double x, double y)
		{
			X = x;
			Y = y;
		}
		public override string ToString()
		{
			return $"{X.ToString().Replace(',','.')}:{Y.ToString().Replace(',','.')}";
		}
		public double[] ToArray()
		{
			var res = new double[2];
			res[0] = X;
			res[1] = Y;
			return res;
		}
	}
}
