using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PyNet.Encoding
{
  internal class BitUtilities
  {
    public static class Boolean
    {
      private const byte TRUE = 1;
      private const byte FALSE = 0;

      public static int ByteLength { get => 1; }

      public static byte[] ToBytes(bool value)
      {
        byte[] ret = new byte[1];
        ret[0] = value ? TRUE : FALSE;
        return ret;
      }
      public static bool FromBytes(byte[] data)
      {
        byte tmp = data[0];
        return tmp != FALSE;
      }
    }

    public static class Int
    {
      public static int ByteLength { get => 4; }

      public static byte[] ToBytes(int value)
      {
        return BitConverter.GetBytes(value);
      }
      public static int FromBytes(byte[] data)
      {
        return BitConverter.ToInt32(data, 0);
      }
    }

    public static class Float
    {
      public static int ByteLength { get => 4; }

      public static byte[] ToBytes(float value)
      {
        return BitConverter.GetBytes(value);
      }
      public static float FromBytes(byte[] data)
      {
        return BitConverter.ToSingle(data, 0);
      }
    }

    public static class Double
    {
      public static int ByteLength { get => 8; }

      public static byte[] ToBytes(double value)
      {
        return BitConverter.GetBytes(value);
      }
      public static double FromBytes(byte[] data)
      {
        return BitConverter.ToDouble(data, 0);
      }
    }

    public static class String
    {
      public static byte[] ToBytes(string value)
      {
        return System.Text.Encoding.ASCII.GetBytes(value);
      }
      public static string FromBytes(byte[] data)
      {
        return System.Text.Encoding.ASCII.GetString(data);
      }
    }
  }
}
