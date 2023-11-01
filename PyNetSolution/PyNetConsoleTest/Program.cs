// See https://aka.ms/new-console-template for more information
using PyNet;
using PyNet.Testing;

Console.WriteLine("Starting listener");

Receiver receiver = new("localhost", 7007);
receiver.ListeningStarted += r => Console.WriteLine($"{r} listening started");
receiver.ListeningStopped += r => Console.WriteLine($"{r} listening stopped");
receiver.ClientConnected += (r, cid) => Console.WriteLine($"{r} client {cid} connected.");
receiver.ClientDisconnected += (r, e) => Console.WriteLine($"{r} client {e.ClientId} disconnected, exception {e.Exception?.Message ?? "None"}");
receiver.MessageReceived += (r, cid, m) => Console.WriteLine($"{r} client {cid} got message {DictToString(m)}");
receiver.Start();

Console.WriteLine("Listener started");

Console.WriteLine("Phase 1 : NET -> Python: Sending");


Sender sender = new("localhost", 8008);
sender.Send(new TestFullBody());

Console.WriteLine("Phase 1 : NET -> Python: Sent");

string DictToString(Dictionary<string, object?> dict)
{
  string ret = string.Join("; ", dict.Select(q => q.Key + ":" + q.Value));
  return ret;
}

Thread.Sleep(100000);