using PyNet.EAsserting;
using PyNet.Encoding;
using PyNet.KeyValues;
using System;
using System.Collections.Generic;
using System.IO.IsolatedStorage;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

namespace PyNet
{
  internal class ReceiverReader
  {
    public delegate void NewMessageHandler(Dictionary<string, object?> message);
    private readonly Socket socket;
    private readonly NewMessageHandler newMessage;

    public ReceiverReader(Socket socket, NewMessageHandler newMessage)
    {
      EAssert.Argument.IsNotNull(socket);
      EAssert.Argument.IsNotNull(newMessage);

      this.socket = socket;
      this.newMessage = newMessage;
    }

    private byte[] ReadData(int dataLen)
    {
      const int BUFFER_SIZE = 1500; //deault MTU size
      byte[] ret = new byte[dataLen];
      byte[] buffer = new byte[BUFFER_SIZE];
      int receivedLen = 0;

      while (receivedLen < dataLen)
      {
        int read = socket.Receive(buffer);
        Array.Copy(buffer, 0, ret, receivedLen, read);
        receivedLen += read;
      }

      EAssert.IsTrue(receivedLen == dataLen);
      return ret;
    }

    internal void ReadOutClient()
    {
      while (true)
      {
        ReadIntro(out int headerLen, out int dataLen);
        KeyValue<string, string>[] header = ReadHeader(headerLen);
        byte[] data = ReadData(dataLen);
        WriteResponse();

        Dictionary<string, object?> message = CreateReceivedMessageDictionary(header, data);

        this.newMessage.Invoke(message);
      }
    }

    private Dictionary<string, object?> CreateReceivedMessageDictionary(KeyValue<string, string>[] header, byte[] data)
    {
      EAssert.Argument.IsNotNull(header, nameof(header));
      EAssert.Argument.IsNotNull(data, nameof(data));

      Dictionary<string, object?> ret = new();

      int dataIndex = 0;
      for (int i = 0; i < header.Length; i++)
      {
        PyNetEncoderManager.DecodeValue(header[i].Value, data, ref dataIndex, out object? value);
        ret[header[i].Key] = value;
      }

      return ret;
    }

    private KeyValue<string, string>[] ReadHeader(int headerLen)
    {
      byte[] buffer = new byte[headerLen];
      int len = socket.Receive(buffer);
      EAssert.IsTrue(len == headerLen);

      string header = BitUtilities.String.FromBytes(buffer);

      List<KeyValue<string, string>> ret = header.Split(";")
        .Select(q =>
        {
          string[] pts = q.Split(':');
          return new KeyValue<string, string>(pts[0], pts[1]);
        })
        .ToList();

      return ret.ToArray();
    }

    private void ReadIntro(out int headerLen, out int dataLen)
    {
      const int INT_SIZE = 4;
      byte[] buffer = new byte[INT_SIZE];
      int len;

      len = socket.Receive(buffer);
      EAssert.IsTrue(len == INT_SIZE);
      headerLen = BitUtilities.Int.FromBytes(buffer);

      len = socket.Receive(buffer);
      EAssert.IsTrue(len == INT_SIZE);
      dataLen = BitUtilities.Int.FromBytes(buffer);
    }

    private void WriteResponse()
    {
      const int RESPONSE_VALUE = 0;
      const int RESPONSE_SIZE = 4;
      byte[] response = BitConverter.GetBytes(RESPONSE_VALUE);
      EAssert.IsTrue(RESPONSE_SIZE == response.Length);
      socket.Send(response);
    }
  }
}
