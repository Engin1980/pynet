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
        q => Regex.IsMatch(q, "s\\d+"),
        q => "s" + q.Length,
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
        q => Regex.IsMatch(q, "b\\d+"),
        q => "b" + q.Length,
        q => q,
        q => int.Parse(q[1..]),
        q => q
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
