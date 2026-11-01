// Investigation only: independent tangent/perpendicular finite-wire integration.
// Fixed-point BigInteger arithmetic, exact binary64 input decomposition.
using System;
using System.Numerics;
public static class Phase2DFieldReference {
    static BigInteger Input(double x, BigInteger s) {
        if (double.IsNaN(x)||double.IsInfinity(x)) throw new ArgumentException("Nonfinite input");
        long bits=BitConverter.DoubleToInt64Bits(x);
        int e=(int)((bits>>52)&2047); long m=bits&0xfffffffffffffL;
        if(e!=0)m|=1L<<52;
        int shift=(e==0 ? -1022 : e-1023)-52;
        BigInteger n=new BigInteger(m)*s;
        n=shift>=0 ? n<<shift : n/(BigInteger.One<<-shift);
        return bits<0 ? -n : n;
    }
    static BigInteger Root(BigInteger n) {
        if(n<0)throw new ArgumentException("Negative square");
        if(n.IsZero)return n;
        int bits=(int)Math.Ceiling(BigInteger.Log(n,2));
        BigInteger x=BigInteger.One<<((bits+2)/2), y=(x+n/x)/2;
        while(y<x){x=y;y=(x+n/x)/2;}return x;
    }
    static string Text(BigInteger n,int digits) {
        string t=BigInteger.Abs(n).ToString().PadLeft(digits+1,'0');
        return (n.Sign<0 ? "-" : "")+t.Substring(0,t.Length-digits)+"."+t.Substring(t.Length-digits);
    }
    public static string[] Field(double[] point,double[][] vertices,double current,int digits) {
        if(digits<50 || point.Length!=3 || vertices.Length<8)throw new ArgumentException("Invalid field reference");
        BigInteger s=BigInteger.Pow(10,digits), coefficient=Input(1e-7,s)*Input(current,s)/s;
        BigInteger[] p=new BigInteger[3], total=new BigInteger[3];
        for(int j=0;j<3;j++)p[j]=Input(point[j],s);
        for(int i=0;i<vertices.Length;i++) {
            BigInteger[] d=new BigInteger[3],r=new BigInteger[3],e=new BigInteger[3],h=new BigInteger[3];
            BigInteger length2=0,dr=0;
            for(int j=0;j<3;j++) {
                d[j]=Input(vertices[(i+1)%vertices.Length][j],s)-Input(vertices[i][j],s);
                r[j]=p[j]-Input(vertices[i][j],s);length2+=d[j]*d[j]/s;dr+=d[j]*r[j]/s;
            }
            if(length2==0)throw new ArgumentException("Degenerate segment");
            BigInteger t=BigInteger.Max(0,BigInteger.Min(s,dr*s/length2)),nearest2=0;
            for(int j=0;j<3;j++){BigInteger v=r[j]-t*d[j]/s;nearest2+=v*v/s;}
            if(nearest2<=Input(1e-8,s))throw new ArgumentException("Near filament");
            BigInteger length=Root(length2*s),z=0,rho2=0;
            for(int j=0;j<3;j++){e[j]=d[j]*s/length;z+=e[j]*r[j]/s;}
            for(int j=0;j<3;j++){h[j]=r[j]-z*e[j]/s;rho2+=h[j]*h[j]/s;}
            if(rho2==0)continue;
            BigInteger end=z-length;
            BigInteger factor=coefficient*s/rho2*(z*s/Root(rho2*s+z*z)-end*s/Root(rho2*s+end*end))/s;
            for(int j=0;j<3;j++){int a=(j+1)%3,b=(j+2)%3;total[j]+=factor*(e[a]*h[b]/s-e[b]*h[a]/s)/s;}
        }
        return new string[]{Text(total[0],digits),Text(total[1],digits),Text(total[2],digits)};
    }
    // Independent binary64 endpoint implementation for comparison, not production NumPy execution.
    public static double[] Endpoint(double[] p,double[][] vv,double current) {
        double[] sum=new double[3];
        for(int i=0;i<vv.Length;i++) {
            double[] a=new double[3],b=new double[3];double n1=0,n2=0,dot=0;
            for(int j=0;j<3;j++){a[j]=p[j]-vv[i][j];b[j]=p[j]-vv[(i+1)%vv.Length][j];n1+=a[j]*a[j];n2+=b[j]*b[j];dot+=a[j]*b[j];}
            n1=Math.Sqrt(n1);n2=Math.Sqrt(n2);double denominator=n1*n2*(n1*n2+dot);
            double factor=denominator>0 ? (n1+n2)/denominator : 0;
            for(int j=0;j<3;j++){int k=(j+1)%3,l=(j+2)%3;sum[j]+=(a[k]*b[l]-a[l]*b[k])*factor;}
        }
        for(int j=0;j<3;j++)sum[j]*=1e-7*current;
        return sum;
    }
}
