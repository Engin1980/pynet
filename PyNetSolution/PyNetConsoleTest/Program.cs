using PyNet;
using System;
using System.Collections.Generic;
using System.ComponentModel.Design;
using System.IO.IsolatedStorage;

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
      sourceDict.Clear();
      sourceDict["ints"] = new int[] { 1, -2 };
      SendDict();
    });

    ret.Add(() =>
    {
      sourceDict.Clear();
      sourceDict["matrix2I"] = new int[][]{
        new int[]{-1, 2},
        new int[]{-3, 4},
        new int[]{-5, 6},
        };
      SendDict();
    });

    ret.Add(() =>
    {
      sourceDict.Clear();
      sourceDict["matrix3I"] = new int[][][]{
        new int[][]{
          new int[]{-1, 2},
        },
        new int[][]{
          new int[]{-3, 4}
        },
        new int[][]{
          new int[]{-5, 6}
        }
        };
      SendDict();
    });

    ret.Add(() =>
    {
      sourceDict.Clear();
      sourceDict["matrix3D"] = new double[][][]{
        new double[][]{
          new double[]{-1.1, 2.2},
        },
        new double[][]{
          new double[]{-3.3, 4.4}
        },
        new double[][]{
          new double[]{-5.5, 6.6}
        }
        };
      SendDict();
    });

    ret.Add(() =>
    {
      sourceDict.Clear();
      sourceDict["matrix2D"] = new double[][]{
        new double[]{-1.1, 2.2},
        new double[]{-3.3, 4.4},
        new double[]{-5.5, 6.6},
        };
      SendDict();
    });

    ret.Add(() =>
    {
      sourceDict.Clear();
      sourceDict["doubles"] = new double[] { 1.1, -2.2 };
      SendDict();
    });

    ret.Add(() =>
    {
      sourceDict.Clear();
      sourceDict["value"] = -5;
      SendDict();
    });

    ret.Add(() =>
    {
      sourceDict.Clear();
      sourceDict["value"] = -5;
      sourceDict["doubles"] = new double[] { 1.1, -2.2 };
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
      else if (valA is double[] doubleA && valB is double[] doubleB)
      {
        if (Enumerable.SequenceEqual(doubleA, doubleB) == false) return false;
      }
      else if (valA is double[][] ddoubleA && valB is double[][] ddoubleB)
      {
        if (ddoubleA.Length != ddoubleB.Length) return false;
        for (int i = 0; i < ddoubleA.Length; i++)
          if (Enumerable.SequenceEqual(ddoubleA[i], ddoubleB[i]) == false) return false;
      }
      else if (valA is double[][][] dddoubleA && valB is double[][][] dddoubleB)
      {
        if (Are3DDoubleArraysEqual(dddoubleA, dddoubleB) == false) return false;
      }
      else if (valA is int[] intA && valB is int[] intB)
      {
        if (Enumerable.SequenceEqual(intA, intB) == false) return false;
      }
      else if (valA is int[][] iintA && valB is int[][] iintB)
      {
        if (iintA.Length != iintB.Length) return false;
        for (int i = 0; i < iintA.Length; i++)
          if (Enumerable.SequenceEqual(iintA[i], iintB[i]) == false) return false;
      }
      else if (valA is int[][][] iiintA && valB is int[][][] iiintB)
      {
        if (Are3DIntArraysEqual(iiintA, iiintB) == false) return false;
      }
      else
      {
        if (object.Equals(valA, valB) == false) return false;
      }
    }

    return true;
  }

  private static bool Are3DIntArraysEqual(int[][][] array1, int[][][] array2)
  {
    int tolerance = 0;
    if (array1.Length != array2.Length)
      return false; // Different lengths in outermost arrays

    for (int i = 0; i < array1.Length; i++)
    {
      if (array1[i].Length != array2[i].Length)
        return false; // Different lengths in the middle arrays

      for (int j = 0; j < array1[i].Length; j++)
      {
        if (array1[i][j].Length != array2[i][j].Length)
          return false; // Different lengths in the innermost arrays

        // Iterate through the innermost arrays
        for (int k = 0; k < array1[i][j].Length; k++)
        {
          int value1 = array1[i][j][k];
          int value2 = array2[i][j][k];

          // Check if the values are within the specified tolerance
          if (Math.Abs(value1 - value2) > tolerance)
            return false; // Values differ
        }
      }
    }

    return true; // All elements are equal within the tolerance
  }

  private static bool Are3DDoubleArraysEqual(double[][][] array1, double[][][] array2)
  {
    double tolerance = 0;
    if (array1.Length != array2.Length)
      return false; // Different lengths in outermost arrays

    for (int i = 0; i < array1.Length; i++)
    {
      if (array1[i].Length != array2[i].Length)
        return false; // Different lengths in the middle arrays

      for (int j = 0; j < array1[i].Length; j++)
      {
        if (array1[i][j].Length != array2[i][j].Length)
          return false; // Different lengths in the innermost arrays

        // Iterate through the innermost arrays
        for (int k = 0; k < array1[i][j].Length; k++)
        {
          double value1 = array1[i][j][k];
          double value2 = array2[i][j][k];

          // Check if the values are within the specified tolerance
          if (Math.Abs(value1 - value2) > tolerance)
            return false; // Values differ
        }
      }
    }

    return true; // All elements are equal within the tolerance
  }
}