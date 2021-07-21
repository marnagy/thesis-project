﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace csharp_console
{
	public struct Log
	{
		public int gen { get; set; }
		public double std { get; set; }
		public double min { get; set; }
		public double avg { get; set; }
		public double max { get; set; }
        public override string ToString()
        {
            return $"{gen};{std:0.000};{min:0.000};{avg:0.000};{max:0.000}";
        }
    
	}
}
