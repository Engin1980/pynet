using PyNet;
using PyNet;
using PyNet.Testing;
using System.Collections.Generic;
using System.ComponentModel.Design;

public static class Program
{
  private static Dictionary<string, object?> sourceDict = new();
  private static List<Action> tests = new();

  public static void Main(string[] args)
  {

    Console.WriteLine("Starting listener");

    tests = CreateTests();

    Receiver receiver = new("localhost", 7007);
    //receiver.ListeningStarted += r => Console.WriteLine($"{r} listening started");
    //receiver.ListeningStopped += r => Console.WriteLine($"{r} listening stopped");
    //receiver.ClientConnected += (r, cid) => Console.WriteLine($"{r} client {cid} connected.");
    //receiver.ClientDisconnected += (r, e) => Console.WriteLine($"{r} client {e.ClientId} disconnected, exception {e.Exception?.Message ?? "None"}");
    receiver.MessageReceived += MessageReceived;

    receiver.Start();

    Console.WriteLine("Listener started");

    StartNextTest();

    Thread.Sleep(100000);
  }

  private static List<Action> CreateTests()
  {
    List<Action> ret = new();

    ret.Add(() =>
    {
      sourceDict["value"] = -5;
      SendDict();
    });

    ret.Add(() =>
    {
      sourceDict["integer_number"] = 10;
      sourceDict["text"] = "Hello there";
      SendDict();
    });

    ret.Add(() =>
    {
      sourceDict["double_number"] = -12824.41313192131924792524d;
      SendDict();
    });

    ret.Add(() =>
    {
      sourceDict.Clear();
      sourceDict["true_or_not"] = true;
      sourceDict["false_or_not"] = false;
      SendDict();
    });

    ret.Clear();
    ret.Add(() =>
    {
      sourceDict.Clear();
      sourceDict["bytes"] = new byte[] { 1, 2, 3, 4, 5, 211, 7, 128, 52, 12, 23 };
      SendDict();
    });

    return ret;
  }

  private static void StartNextTest()
  {
    if (tests.Count == 0)
    {
      Console.WriteLine("All tests completed.");
      return;
    }

    Action test = tests[0];
    tests.RemoveAt(0);
    Console.WriteLine("* * * Starting next test");
    test.Invoke();
  }

  private static void MessageReceived(Receiver sender, int clientId, Dictionary<string, object?> message)
  {
    Console.WriteLine("Message received");
    Console.WriteLine("Source: " + DictToString(sourceDict));
    Console.WriteLine("Messag: " + DictToString(message));
    if (AreDictionariesEqual(sourceDict, message))
      Console.WriteLine("Test passed ok");
    else
    {
      Console.WriteLine("Test Match  F A I L E D.");
      Console.WriteLine("Press any key");
      Console.ReadKey();
    }

    StartNextTest();

  }

  private static void SendDict()
  {
    Console.WriteLine("Sending dict " + DictToString(sourceDict));
    Sender sender = new("localhost", 8008);
    sender.Send(sourceDict);
    Console.WriteLine("\tdone");
  }

  private static string DictToString(Dictionary<string, object?> dict)
  {
    string ret = string.Join("; ", dict.Select(q => q.Key + ":" + q.Value));
    return ret;
  }

  private static bool AreDictionariesEqual(Dictionary<string, object?> dctA, Dictionary<string, object?> dctB)
  {
    if (dctA.Count != dctB.Count)
      return false;

    foreach (var entry in dctA)
    {
      if (dctB.ContainsKey(entry.Key) == false) return false;
      object? valA = entry.Value;
      object? valB = dctB[entry.Key];
      if (valA is byte[] byteA && valB is byte[] byteB)
      {
        if (Enumerable.SequenceEqual(byteA, byteB) == false) return false;
      }
      else if (object.Equals(valA, valB) == false) return false;
    }

    return true;
  }
}