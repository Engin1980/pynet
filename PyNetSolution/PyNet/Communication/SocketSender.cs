using Microsoft.VisualBasic;
using PyNet.EAsserting;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;

namespace PyNet.Communication
{
  public class SocketSender : IDataSender
  {
    public const int RESPONSE_SIZE = 4;

    public string Host { get; set; }
    public int Port { get; set; }
    private Socket? socket;

    public SocketSender(string host, int port)
    {
      EAssert.Argument.IsNonEmptyString(host, nameof(host));
      EAssert.Argument.IsTrue(port > 0, nameof(port), "Must be > 0");

      Host = host!;
      Port = port;
    }

    public void Send(byte[] data)
    {
      EAssert.IsNotNull(this.socket, "Socket is not opened.");

      if (data != null)
        this.socket!.Send(data);

      byte[] resp = new byte[RESPONSE_SIZE];
      int read = this.socket!.Receive(resp);
      EAssert.IsTrue(read == RESPONSE_SIZE);
    }

    public void Open()
    {
      EAssert.IsNull(this.socket, "Socket is already opened.");
      this.socket = CreateAndBindTransmitterSocket();
    }

    public void Close(bool checkIsOpened = false)
    {
      if (checkIsOpened) EAssert.IsNotNull(this.socket, "Socket is not opened, cannot be closed.");

      if (socket != null)
        this.socket.Close();

      this.socket = null;
    }

    private Socket CreateAndBindTransmitterSocket()
    {
      Console.WriteLine("Socket only localhost demo.");
      IPAddress ipAddress = IPAddress.Loopback;
      IPEndPoint remoteEndPoint = new(ipAddress, this.Port);

      Socket ret = new(ipAddress.AddressFamily, SocketType.Stream, ProtocolType.Tcp);
      ret.Connect(remoteEndPoint);
      return ret;
    }

  }
}
