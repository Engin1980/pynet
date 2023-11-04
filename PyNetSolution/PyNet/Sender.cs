using PyNet.Communication;
using PyNet.EAsserting;
using PyNet.Encoding;
using PyNet.KeyValues;
using System.Reflection;

namespace PyNet
{
  public class Sender : IWithLog
  {
    public event IWithLog.LogHandler? Log;

    public string Host { get; private set; }

    public int Port { get; private set; }

    public Sender(string host, int port)
    {
      EAssert.Argument.IsNonEmptyString(host, nameof(host));
      EAssert.Argument.IsTrue(port > 0, nameof(port), "Must be > 0");

      Host = host!;
      Port = port;
    }
    public static Dictionary<string, object?> CreateDictionaryFromObject(object obj)
    {
      Dictionary<string, object?> ret = new();
      Type type = obj.GetType();
      type.GetProperties().ToList().ForEach(q => ret.Add(q.Name, q.GetValue(obj)));
      return ret;
    }

    public void Send(object obj)
    {
      EAssert.Argument.IsNotNull(obj, nameof(obj));
      var dict = CreateDictionaryFromObject(obj);
      Send(dict);
    }

    public void Send(Dictionary<string, object?> values)
    {
      string header;
      byte[] data;
      try
      {
        EncodeMessage(values, out header, out data);
      }
      catch (Exception ex)
      {
        throw new PyNetException("Failed to convert dictionary to message.", ex);
      }

      SendViaPort(header, data);
    }

    internal static void EncodeMessage(Dictionary<string, object?> values, out string header, out byte[] data)
    {
      KeyValue<string, string>[] h = new KeyValue<string, string>[values.Count];
      byte[][] d = new byte[values.Count][];

      int index = 0;
      foreach (var entry in values)
      {
        PyNetEncoderManager.EncodeValue(entry.Value, out string tmpType, out byte[] tmpData);
        h[index] = new KeyValue<string, string>(entry.Key, tmpType);
        d[index] = tmpData;
        index++;
      }

      header = string.Join(";", h.Select(q => $"{q.Key}:{q.Value}"));
      data = JoinByteArrays(d);
    }

    private static byte[] JoinByteArrays(byte[][] d)
    {
      byte[] ret = new byte[d.Sum(q => q.Length)];
      int curIndex = 0;
      for (int i = 0; i < d.Length; i++)
      {
        Array.Copy(d[i], 0, ret, curIndex, d[i].Length);
        curIndex += d[i].Length;
      }
      return ret;
    }

    private void SendViaPort(string header, byte[] dataBytes)
    {
      byte[] headerBytes = BitUtilities.String.ToBytes(header);
      byte[] headerLen = BitUtilities.Int.ToBytes(headerBytes.Length);
      byte[] dataLen = BitUtilities.Int.ToBytes(dataBytes.Length);

      SocketSender ss = new(this.Host, this.Port);

      byte[] buffer = new byte[headerLen.Length + dataLen.Length + headerBytes.Length + dataBytes.Length];
      headerLen.CopyTo(buffer, 0);
      dataLen.CopyTo(buffer, headerLen.Length);
      headerBytes.CopyTo(buffer, headerLen.Length + dataLen.Length);
      dataBytes.CopyTo(buffer, headerLen.Length + dataLen.Length + headerBytes.Length);

      ss.Open();
      ss.Send(buffer);
      ss.Close();
    }
  }
}