// Independent fixed-point investigation of archived binary64 inputs.
// No NumPy, BLAS, SciPy, production metric helper or geometry regeneration.
using System;
using System.Numerics;
using System.Collections.Generic;

public static class Phase2DReference {
    static BigInteger Input(double x, BigInteger scale) {
        if (double.IsNaN(x) || double.IsInfinity(x)) throw new ArgumentException("Nonfinite input");
        long bits = BitConverter.DoubleToInt64Bits(x);
        int exponent = (int)((bits >> 52) & 2047);
        long mantissa = bits & 0xfffffffffffffL;
        if (exponent != 0) mantissa |= 1L << 52;
        int shift = (exponent == 0 ? -1022 : exponent - 1023) - 52;
        BigInteger value = new BigInteger(mantissa) * scale;
        value = shift >= 0 ? value << shift : value / (BigInteger.One << -shift);
        return bits < 0 ? -value : value;
    }
    static BigInteger Sqrt(BigInteger n) {
        if (n < 0) throw new ArgumentException("Negative square");
        if (n.IsZero) return n;
        BigInteger x = n, y = (x + 1) / 2;
        while (y < x) { x = y; y = (x + n / x) / 2; }
        return x;
    }
    static string Text(BigInteger n, int digits) {
        string sign = n.Sign < 0 ? "-" : "";
        string s = BigInteger.Abs(n).ToString().PadLeft(digits + 1, '0');
        return sign + s.Substring(0, s.Length-digits) + "." + s.Substring(s.Length-digits);
    }
    public static string Ratio(double[][] matrix, double[] b, double[] w,
                               double[][] currents, int digits) {
        BigInteger scale = BigInteger.Pow(10, digits);
        BigInteger[] norms = new BigInteger[3];
        for (int k=0; k<3; k++) {
            BigInteger energy = BigInteger.Zero;
            for (int i=0; i<b.Length; i++) {
                BigInteger residual = Input(b[i], scale);
                for (int j=0; j<currents[k].Length; j++)
                    residual += Input(matrix[i][j], scale)*Input(currents[k][j], scale)/scale;
                energy += Input(w[i], scale)*residual*residual/scale/scale;
            }
            norms[k] = Sqrt(energy*scale);
        }
        BigInteger denominator = norms[1]-norms[0];
        if (BigInteger.Abs(denominator) <= scale/BigInteger.Pow(10,15)) return null;
        return Text((norms[1]-norms[2])*scale/denominator, digits);
    }
}
