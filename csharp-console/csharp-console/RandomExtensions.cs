using System;
using System.Collections;
using System.Collections.Generic;

namespace csharp_console
{
    /// <summary>
    /// Some extension methods for <see cref="Random"/> for creating a few more kinds of random stuff.
    /// </summary>
    public static class RandomExtensions
    {
        /// <summary>
        ///   Generates normally distributed numbers. Each operation makes two Gaussians for the price of one, and apparently they can be cached or something for better performance, but who cares.
        /// </summary>
        /// <param name="r"></param>
        /// <param name = "mu">Mean of the distribution</param>
        /// <param name = "sigma">Standard deviation</param>
        /// <returns></returns>
        public static double NextGaussian(this Random r, double mu = 0, double sigma = 1)
        {
            // while loops so variable isn't 0
            // so Log of variable is not NaN
            double u1 = r.NextDouble();
            double u2 = r.NextDouble();
            while ( u1 == 0d )
            {
                u1 = r.NextDouble();
            }
            while ( u2 == 0d )
            {
                u2 = r.NextDouble();
            }

            var rand_std_normal = Math.Sqrt(-2.0 * Math.Log(u1)) *
                                Math.Sin(2.0 * Math.PI * u2);

            var rand_normal = mu + sigma * rand_std_normal;

            return rand_normal;
        }
    }
}