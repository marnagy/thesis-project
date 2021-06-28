using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console
{
	public class Heap<T> where T : IComparable<T>, new()
	{
		readonly Comparison<T> _keyFunc;
		public int Count { get => GetCount(); }
		readonly List<T> nodes;
		public Heap(Comparison<T> keyFunc)
		{
			_keyFunc = keyFunc;
			nodes = new List<T>();
			nodes.Add( new T() );
		}

		public void Add(T item)
		{
			if (item == null)
				return;

			nodes.Add(item);

			// bubble up
			int index = nodes.Count - 1;
			while ( index > 1 )
			{ 
				int parentIndex = index / 2;
				//Console.WriteLine($"Index: {index}, parentIndex: {parentIndex}");
				if ( _keyFunc(nodes[index], nodes[parentIndex]) <= 0)
				{
					T temp = nodes[index];
					nodes[index] = nodes[parentIndex];
					nodes[parentIndex] = temp;
					index = parentIndex;
				}
				else
					break;
			}
		}
		public T Get()
		{
			if (nodes.Count == 2)
			{
				T result = nodes[1];
				nodes.RemoveAt(1);
				return result;
			}
			else
			{
				T result = nodes[1];
				T temp;

				temp = result;
				nodes[1] = nodes[ nodes.Count - 1 ];
				nodes[ nodes.Count - 1 ] = result;

				nodes.RemoveAt(nodes.Count - 1);

				T item = nodes[1];
				// bubble down
				int index = 1;
				while ( index*2 < nodes.Count)
				{
					int bestIndex = index;
					if ( _keyFunc(nodes[index], nodes[index*2]) >= 0)
						bestIndex = index*2;

					if ( index*2 + 1 < nodes.Count && _keyFunc(nodes[bestIndex], nodes[index*2 + 1]) >= 0 )
						bestIndex = index*2 + 1;

					if (bestIndex == index)
						break;
					else
					{
						temp = nodes[index];
						nodes[index] = nodes[bestIndex];
						nodes[bestIndex] = temp;
						index = bestIndex;
					}
				}
				return result;
			}
		}
		private int GetCount()
		{
			return nodes.Count - 1;
		}
		public bool Check()
		{
			bool checkStatus = true;
			for (int i = 1; i < nodes.Count; i++)
			{
				var n = nodes[i];

				if (nodes.Count > 2*i && _keyFunc(nodes[i], nodes[i*2]) > 0 )
				{
					checkStatus = false;
					return checkStatus;
				}

				if (nodes.Count > 2*i+1 && _keyFunc(nodes[i], nodes[2*i+1]) > 0 )
				{
					checkStatus = false;
					return checkStatus;
				}
			}
			return checkStatus;
		}
	}
}
