using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using PyNet.EAsserting;

namespace PyNet.Encoding
{
  internal class PyNetEncoderManager
  {
    internal static class Encoders
    {
      public static PyNetEncoder<object?> NullEncoder = new(
        q => q == null,
        q => q == "n",
        q => "n",
        q => Array.Empty<byte>(),
        q => 0,
        q => null
      );

      public static PyNetEncoder<string> StringEncoder = new PyNetEncoder<string>(
        q => q is string,
        q => Regex.IsMatch(q, "^s\\d+"),
        q => $"s{q.Length}",
        q => BitUtilities.String.ToBytes(q),
        q => int.Parse(q[1..]),
        q => BitUtilities.String.FromBytes(q)
        );

      internal static PyNetEncoder<int> IntEncoder = new(
        q => q is int,
        q => q == "i",
        q => "i",
        q => BitUtilities.Int.ToBytes(q),
        q => BitUtilities.Int.ByteLength,
        q => BitUtilities.Int.FromBytes(q)
        );

      // float cannot be sent; on Python side there is no way to distinquish which type should be sent
      internal static PyNetEncoder<double> DoubleEncoder = new(
        q => q is double,
        q => q == "d",
        q => "d",
        q => BitUtilities.Double.ToBytes(q),
        q => BitUtilities.Double.ByteLength,
        q => BitUtilities.Double.FromBytes(q)
        );

      internal static PyNetEncoder<bool> BoolEncoder = new(
        q => q is bool,
        q => q == "b",
        q => "b",
        q => BitUtilities.Boolean.ToBytes(q),
        q => BitUtilities.Boolean.ByteLength,
        q => BitUtilities.Boolean.FromBytes(q)
        );

      internal static PyNetEncoder<byte[]> ByteArrayEncoder = new(
        q => q is byte[],
        q => Regex.IsMatch(q, "^b\\d+"),
        q => $"b{q.Length}",
        q => q,
        q => int.Parse(q[1..]),
        q => q
        );

      internal static PyNetEncoder<double[]> DoubleArrayEncoder = new(
        q => q is double[],
        q => Regex.IsMatch(q, "^d\\d+"),
        q => $"d{q.Length * BitUtilities.Double.ByteLength}",
        q => q.SelectMany(d => BitUtilities.Double.ToBytes(d)).ToArray(),
        q => int.Parse(q[1..]),
        q => Enumerable
          .Range(0, q.Length / sizeof(double))
          .Select(offset => BitConverter.ToDouble(q, offset * sizeof(double)))
          .ToArray()
        );

      internal static PyNetEncoder<double[][]> Matrix2DEncoder = new(
        q => q is double[][],
        q => Regex.IsMatch(q, "^md\\d+"),
        q => $"md{q.Length * q[0].Length * BitUtilities.Double.ByteLength + 2 * BitUtilities.Int.ByteLength}",
        q =>
        {
          byte[] dimA = BitUtilities.Int.ToBytes(q.Length);
          byte[] dimB = BitUtilities.Int.ToBytes(q[0].Length);
          List<byte[]> rows = q.SelectMany(d => d.Select(p => BitUtilities.Double.ToBytes(p)).ToList()).ToList();
          byte[] ret = dimA.Concat(dimB).ToArray();
          rows.ForEach(q => ret = ret.Concat(q).ToArray());
          return ret;
        },
        q => int.Parse(q[2..]),
        q =>
        {
          double[][] ret;
          byte[] tmp;

          int INT_LEN = BitUtilities.Int.ByteLength;
          int DBL_LEN = BitUtilities.Double.ByteLength;

          tmp = q[0..INT_LEN];
          int dimA = BitUtilities.Int.FromBytes(tmp);
          tmp = q[INT_LEN..(2 * INT_LEN)];
          int dimB = BitUtilities.Int.FromBytes(tmp);

          ret = new double[dimA][];
          int BLCK_LEN = dimB * DBL_LEN;
          tmp = new byte[BLCK_LEN];
          for (int i = 0; i < dimA; i++)
          {
            System.Buffer.BlockCopy(q, 2 * INT_LEN + i * BLCK_LEN, tmp, 0, BLCK_LEN);
            double[] part = Enumerable
              .Range(0, tmp.Length / sizeof(double))
              .Select(offset => BitConverter.ToDouble(tmp, offset * sizeof(double)))
              .ToArray();
            ret[i] = part;
          }

          return ret;
        }
        );

      internal static PyNetEncoder<double[][][]> Matrix3DEncoder = new(
        q => q is double[][][],
        q => Regex.IsMatch(q, "^mmd\\d+"),
        q => $"mmd{q.Length * q[0].Length * q[0][0].Length * BitUtilities.Double.ByteLength + 3 * BitUtilities.Int.ByteLength}",
        q =>
        {
          byte[] dimA = BitUtilities.Int.ToBytes(q.Length);
          byte[] dimB = BitUtilities.Int.ToBytes(q[0].Length);
          byte[] dimC = BitUtilities.Int.ToBytes(q[0][0].Length);
          List<byte[]> rows = new();
          for (int i = 0; i < q.Length; i++)
            for (int j = 0; j < q[0].Length; j++)
              rows.Add(q[i][j].SelectMany(q => BitUtilities.Double.ToBytes(q)).ToArray());

          byte[] ret = dimA.Concat(dimB).Concat(dimC).ToArray();
          rows.ForEach(q => ret = ret.Concat(q).ToArray());
          return ret;
        },
        q => int.Parse(q[3..]),
        q =>
        {
          double[][][] ret;
          byte[] tmp;

          int INT_LEN = BitUtilities.Int.ByteLength;
          int DBL_LEN = BitUtilities.Double.ByteLength;

          tmp = q[0..INT_LEN];
          int dimA = BitUtilities.Int.FromBytes(tmp);
          tmp = q[INT_LEN..(2 * INT_LEN)];
          int dimB = BitUtilities.Int.FromBytes(tmp);
          tmp = q[(2 * INT_LEN)..(3 * INT_LEN)];
          int dimC = BitUtilities.Int.FromBytes(tmp);

          ret = new double[dimA][][];
          int BLCK_LEN = dimC * DBL_LEN;
          tmp = new byte[BLCK_LEN];
          for (int i = 0; i < dimA; i++)
          {
            ret[i] = new double[dimB][];
            for (int j = 0; j < dimB; j++)
            {
              System.Buffer.BlockCopy(q, 3 * INT_LEN + ((i * dimB) + j) * BLCK_LEN, tmp, 0, BLCK_LEN);
              double[] part = Enumerable
                .Range(0, tmp.Length / sizeof(double))
                .Select(offset => BitConverter.ToDouble(tmp, offset * sizeof(double)))
                .ToArray();
              ret[i][j] = part;
            }
          }

          return ret;
        }
        );

      internal static PyNetEncoder<int[]> IntArrayEncoder = new(
        q => q is int[],
        q => Regex.IsMatch(q, "^i\\d+"),
        q => $"i{q.Length * BitUtilities.Int.ByteLength}",
        q => q.SelectMany(d => BitUtilities.Int.ToBytes(d)).ToArray(),
        q => int.Parse(q[1..]),
        q => Enumerable
          .Range(0, q.Length / sizeof(int))
          .Select(offset => BitConverter.ToInt32(q, offset * sizeof(int)))
          .ToArray()
        );

      internal static PyNetEncoder<int[][]> Matrix2IEncoder = new(
        q => q is int[][],
        q => Regex.IsMatch(q, "^mi\\d+"),
        q => $"mi{q.Length * q[0].Length * BitUtilities.Int.ByteLength + 2 * BitUtilities.Int.ByteLength}",
        q =>
        {
          byte[] dimA = BitUtilities.Int.ToBytes(q.Length);
          byte[] dimB = BitUtilities.Int.ToBytes(q[0].Length);
          List<byte[]> rows = q.SelectMany(d => d.Select(p => BitUtilities.Int.ToBytes(p)).ToList()).ToList();
          byte[] ret = dimA.Concat(dimB).ToArray();
          rows.ForEach(q => ret = ret.Concat(q).ToArray());
          return ret;
        },
        q => int.Parse(q[2..]),
        q =>
        {
          int[][] ret;
          byte[] tmp;

          int INT_LEN = BitUtilities.Int.ByteLength;

          tmp = q[0..INT_LEN];
          int dimA = BitUtilities.Int.FromBytes(tmp);
          tmp = q[INT_LEN..(2 * INT_LEN)];
          int dimB = BitUtilities.Int.FromBytes(tmp);

          ret = new int[dimA][];
          int BLCK_LEN = dimB * INT_LEN;
          tmp = new byte[BLCK_LEN];
          for (int i = 0; i < dimA; i++)
          {
            System.Buffer.BlockCopy(q, 2 * INT_LEN + i * BLCK_LEN, tmp, 0, BLCK_LEN);
            int[] part = Enumerable
              .Range(0, tmp.Length / sizeof(int))
              .Select(offset => BitConverter.ToInt32(tmp, offset * sizeof(int)))
              .ToArray();
            ret[i] = part;
          }

          return ret;
        }
        );

      internal static PyNetEncoder<int[][][]> Matrix3IEncoder = new(
        q => q is int[][][],
        q => Regex.IsMatch(q, "^mmi\\d+"),
        q => $"mmi{q.Length * q[0].Length * q[0][0].Length * BitUtilities.Int.ByteLength + 3 * BitUtilities.Int.ByteLength}",
        q =>
        {
          byte[] dimA = BitUtilities.Int.ToBytes(q.Length);
          byte[] dimB = BitUtilities.Int.ToBytes(q[0].Length);
          byte[] dimC = BitUtilities.Int.ToBytes(q[0][0].Length);
          List<byte[]> rows = new();
          for (int i = 0; i < q.Length; i++)
            for (int j = 0; j < q[0].Length; j++)
              rows.Add(q[i][j].SelectMany(q => BitUtilities.Int.ToBytes(q)).ToArray());

          byte[] ret = dimA.Concat(dimB).Concat(dimC).ToArray();
          rows.ForEach(q => ret = ret.Concat(q).ToArray());
          return ret;
        },
        q => int.Parse(q[3..]),
        q =>
        {
          int[][][] ret;
          byte[] tmp;

          int INT_LEN = BitUtilities.Int.ByteLength;

          tmp = q[0..INT_LEN];
          int dimA = BitUtilities.Int.FromBytes(tmp);
          tmp = q[INT_LEN..(2 * INT_LEN)];
          int dimB = BitUtilities.Int.FromBytes(tmp);
          tmp = q[(2 * INT_LEN)..(3 * INT_LEN)];
          int dimC = BitUtilities.Int.FromBytes(tmp);

          ret = new int[dimA][][];
          int BLCK_LEN = dimC * INT_LEN;
          tmp = new byte[BLCK_LEN];
          for (int i = 0; i < dimA; i++)
          {
            ret[i] = new int[dimB][];
            for (int j = 0; j < dimB; j++)
            {
              System.Buffer.BlockCopy(q, 3 * INT_LEN + ((i * dimB) + j) * BLCK_LEN, tmp, 0, BLCK_LEN);
              int[] part = Enumerable
                .Range(0, tmp.Length / sizeof(int))
                .Select(offset => BitConverter.ToInt32(tmp, offset * sizeof(int)))
                .ToArray();
              ret[i][j] = part;
            }
          }

          return ret;
        }
        );
    }

    internal static void EncodeValue(object? value, out string tmpType, out byte[] tmpData)
    {
      object encoder = GetEncoderByValue(value);
      EncodeValueWithEncoder(encoder, value, out tmpType, out tmpData);
    }

    private static void EncodeValueWithEncoder(object encoder, object? value, out string type, out byte[] data)
    {
      type = InvokeFuncOne<string>(encoder, "ToTypeId", value) ?? throw new ApplicationException("Unexpected null");
      data = InvokeFuncOne<byte[]>(encoder, "ToData", value) ?? throw new ApplicationException("Unexpected null");
    }

    private static R? InvokeFuncOne<R>(object source, string propName, params object?[] parameters)
    {
      var type = source.GetType();
      var propInfo = type.GetProperty(propName) ?? throw new ApplicationException($"Unble to find property {propName} on type {type.Name}.");
      var propValue = propInfo.GetValue(source, null) ?? throw new ApplicationException($"{type.Name}.{propName} returned null.");

      var invokeMethod = propValue.GetType().GetMethod("Invoke") ?? throw new ApplicationException("Unexpected null");
      var tmp = invokeMethod.Invoke(propValue, parameters);
      R? ret = (R?)tmp;
      return ret;
    }

    private static List<object> GetEncoders()
    {
      var ret = typeof(Encoders)
        .GetFields(System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public)
        .Select(q => q.GetValue(null) ?? throw new ApplicationException("Unexpected null"))
        .ToList();

      return ret;
    }


    private static object GetEncoderByValue(object? value)
    {
      object ret;
      List<object> encoders = GetEncoders();

      object encoder = encoders.FirstOrDefault(q => InvokeFuncOne<bool>(q, "AcceptsValue", value))
        ?? throw new PyNetException($"Failed to find appropriate encoder for ${value?.GetType().Name ?? "null"} (val={value}).");

      ret = encoder;
      return ret;
    }

    internal static void DecodeValue(string typeId, byte[] data, ref int dataIndex, out object? value)
    {
      object encoder = GetWrappedEncoderByTypeId(typeId);
      DecodeValueWithEncoder(encoder, typeId, data, ref dataIndex, out value);
    }

    private static void DecodeValueWithEncoder(object encoder, string typeId, byte[] data, ref int dataIndex, out object? value)
    {
      int dataLen = InvokeFuncOne<int>(encoder, "ToByteLen", typeId);
      byte[] buffer = new byte[dataLen];
      Array.Copy(data, dataIndex, buffer, 0, dataLen);
      dataIndex += dataLen;

      value = InvokeFuncOne<object?>(encoder, "ToValue", buffer);
    }

    private static object GetWrappedEncoderByTypeId(string typeId)
    {
      object ret;
      List<object> encoders = GetEncoders();

      object encoder = encoders.FirstOrDefault(q => InvokeFuncOne<bool>(q, "AcceptsTypeId", typeId))
        ?? throw new PyNetException($"Failed to find appropriate encoder for type identifier ${typeId}.");

      ret = encoder;
      return ret;
    }
  }
}
