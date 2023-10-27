using Microsoft.VisualBasic;
using PyNet.EAsserting;
using PyNet.Encoding;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Sockets;
using System.Runtime.CompilerServices;
using System.Security.AccessControl;
using System.Text;
using System.Threading.Tasks;

namespace PyNet
{
  public class Receiver
  {
    private enum ListenerState
    {
      Listening,
      Aborting,
      Stopped
    }

    public class ClientDisconnectedEventArgs
    {
      public ClientDisconnectedEventArgs(int clientId)
      {
        ClientId = clientId;
        Exception = null;
      }

      public ClientDisconnectedEventArgs(int clientId, Exception? exception)
      {
        ClientId = clientId;
        Exception = exception;
      }

      public int ClientId { get; private set; }
      public Exception? Exception { get; private set; }
      public bool IsOk { get => this.Exception == null; }
    }

    #region Delegates

    /// <summary>
    /// Delegate for <see cref="ClientConnected" /> event
    /// </summary>
    /// <param name="sender">Sender</param>
    /// <param name="clientId">ID of client</param>
    public delegate void ClientConnectedDelegate(Receiver sender, int clientId);
    /// <summary>
    /// Delegate for <see cref="ClientDisconnected" /> event
    /// </summary>
    /// <param name="sender">Sender</param>
    /// <param name="closeInfo">ID of client</param>
    public delegate void ClientDisconnectedDelegate(Receiver sender, ClientDisconnectedEventArgs e);
    /// <summary>
    /// Delegate for <see cref="MessageReceivedDelegate" /> event
    /// </summary>
    /// <param name="sender">Sender</param>
    /// <param name="clientId">ID of client</param>
    /// <param name="dataBlock">Obtained datablock</param>
    public delegate void MessageReceivedDelegate(Receiver sender, int clientId, Dictionary<string, object?> dataBlock);
    //TODO remove second parameter clientId as it is already included in DataBlock

    /// <summary>
    /// Delegate for <see cref="ListeningStarted" /> and <see cref="ListeningStopped" /> events
    /// </summary>
    /// <param name="sender">Sender</param>
    public delegate void ReceiverDelegate(Receiver sender);

    #endregion

    #region Events

    /// <summary>
    /// Invoked on a new client connection.
    /// </summary>
    public event ClientConnectedDelegate? ClientConnected;
    /// <summary>
    /// Invoked on a client disconnection.
    /// </summary>
    public event ClientDisconnectedDelegate? ClientDisconnected;
    /// <summary>
    /// Invoked on an incoming message data.
    /// </summary>
    public event MessageReceivedDelegate? MessageReceived;

    /// <summary>
    /// Invoked when listening has started.
    /// </summary>
    /// <seealso cref="MeCoM.Receiving.Receiver.Start(int)"/>
    public event ReceiverDelegate? ListeningStarted;
    /// <summary>
    /// Invoked when listening has stopped.
    /// </summary>
    /// <seealso cref="MeCoM.Receiving.Receiver.StopWhenAble"/>
    public event ReceiverDelegate? ListeningStopped;

    #endregion


    private readonly List<Socket> clients = new();
    private Socket? listener = null;
    private int numberOfConcurentConnections = 10;
    private ListenerState state = ListenerState.Stopped;
    private Thread? thread = null;
    private static int nextClientId = 1;

    /// <summary>
    /// Returns number of current clients.
    /// </summary>
    public int ClientCount { get => this.clients.Count; }

    /// <summary>
    /// Target host IP address.
    /// </summary>
    public string Host { get; private set; }
    /// <summary>
    /// Check if the receiver is started and running.
    /// </summary>
    /// <seealso cref="MeCoM.Receiving.Receiver.Start(int)"/>
    /// <seealso cref="MeCoM.Receiving.Receiver.StopWhenAble"/>
    public bool IsRunning { get => this.state != ListenerState.Stopped; }
    /// <summary>
    /// Target host port number.
    /// </summary>
    public int Port { get; private set; }

    /// <summary>
    /// Creates a new instance for specified host or port.
    /// </summary>
    /// <param name="host">Host IP address</param>
    /// <param name="port">Host port number</param>
    /// <exception cref="Exception">Thrown at any error (see causes).</exception>
    public Receiver(string host, int port)
    {
      EAssert.Argument.IsNonEmptyString(host);
      EAssert.Argument.IsTrue(port > 0);

      this.Host = host;
      this.Port = port;
    }

    /// <summary>
    /// Starts listening on receiver.
    /// </summary>
    /// <param name="numberOfConcurentConnections">Maximal number of clients.</param>
    public void Start(int numberOfConcurentConnections = 10)
    {
      EAssert.Argument.IsTrue(numberOfConcurentConnections > 0);
      lock (this)
      {
        if (this.state != ListenerState.Stopped) return;
        else this.state = ListenerState.Listening;
      }

      this.numberOfConcurentConnections = numberOfConcurentConnections;

      this.thread = new Thread(this.DoListening);
      this.thread.Start();
    }

    /// <summary>
    /// Stops listening on receiver.
    /// Listening is not stopped immediatelly, but asks for close all the opened clients and then closes itself.
    /// </summary>
    public void StopWhenAble()
    {
      this.state = ListenerState.Aborting;
      this.WithLockedClients(() => this.clients.ForEach(q => this.ShutdownAndCloseSocket(q)));
      this.ShutdownAndCloseSocket(this.listener);
    }

    /// <summary>
    /// Returns Receiver hash as a result.
    /// </summary>
    /// <returns></returns>
    public override string ToString()
    {
      return "Receiver_" + this.GetHashCode().ToString();
    }

    #region Private Methods

    private Socket CreateAndBindListenerSocket()
    {
      Console.WriteLine("Loopback hardly fixed here.");
      IPAddress ipAddress = IPAddress.Loopback; // host.AddressList[0];
      IPEndPoint localEndPoint = new(ipAddress, this.Port);

      Socket ret = new(ipAddress.AddressFamily, SocketType.Stream, ProtocolType.Tcp);
      ret.Bind(localEndPoint);
      return ret;
    }

    private void DoListening()
    {
      this.listener = CreateAndBindListenerSocket();
      this.listener.Listen(this.numberOfConcurentConnections);
      this.ListeningStarted?.Invoke(this);

      while (this.state == ListenerState.Listening)
      {
        try
        {
          Socket handler = this.listener.Accept();
          this.WithLockedClients(() => this.clients.Add(handler));
          int clientId = nextClientId++;
          ClientConnected?.Invoke(this, clientId);
          this.ReadOutClient(handler, clientId, out ClientDisconnectedEventArgs e);
          ClientDisconnected?.Invoke(this, e);
          this.WithLockedClients(() => this.clients.Remove(handler));
        }
        catch (SocketException ex)
        {
          EAssert.IsTrue(
            ex.SocketErrorCode == SocketError.Interrupted,
            $"Listening-Socket-Accept interrupted with unexpected SocketErrorCode {ex.SocketErrorCode}.");
          break;
        }
      }

      this.listener = null;
      this.state = ListenerState.Stopped;
      this.ListeningStopped?.Invoke(this);
    }

    private void ReadOutClient(Socket socket, int clientId, out ClientDisconnectedEventArgs e)
    {
      try
      {
        ReceiverReader rr = new(socket, dt => RaiseMessageReceived(clientId, dt));
        rr.ReadOutClient();
        e = new ClientDisconnectedEventArgs(clientId);
      }
      catch (Exception ex)
      {
        e = new ClientDisconnectedEventArgs(clientId, ex);
      }
    }

    private void RaiseMessageReceived(int clientId, Dictionary<string, object?> msg)
    {
      ThreadStart ts = new(() => MessageReceived?.Invoke(this, clientId, msg));
      Thread t = new(ts);
      t.Start();
    }

    private Dictionary<string, object?> CreateReceivedMessageDictionary(Dictionary<string, string> header, byte[] data)
    {
      throw new NotImplementedException();
    }

    private void ShutdownAndCloseSocket(Socket? socket)
    {
      if (socket == null) return;
      try
      {
        socket.Shutdown(SocketShutdown.Both);
      }
      catch (SocketException ex)
      {
        EAssert.IsTrue(
          ex.SocketErrorCode == SocketError.NotConnected,
          $"Receiver-Socket closed with unexpected error code {ex.SocketErrorCode}.");
      }
      finally
      {
        socket.Close();
      }
    }

    private void WithLockedClients(Action action)
    {
      lock (this.clients)
      {
        action.Invoke();
      }
    }

    #endregion

  }
}
