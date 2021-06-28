using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console.Graph
{
	public class ReadOnlyNode
	{
		public readonly ulong Id;
		public readonly PointD Point;
		public readonly IReadOnlySet<ReadOnlyEdge> OutEdges;

		public ReadOnlyNode(ulong id, PointD point, IReadOnlySet<ReadOnlyEdge> outEdges)
		{
			Id = id;
			Point = point;
			OutEdges = outEdges;
		}
	}
}
