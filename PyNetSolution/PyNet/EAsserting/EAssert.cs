using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Sockets;
using System.Text;
using System.Threading.Tasks;

namespace PyNet.EAsserting
{
  public static class EAssert
  {
    internal static void IsNotNull(object? obj, string message = "EAssert object is null.")
    {
      if (obj == null) throw new EAssertException(message);
    }

    internal static void IsNull(object? obj, string message = "EAssert object is not null.")
    {
      if (obj != null) throw new EAssertException(message);
    }

    internal static void IsTrue(bool condition, string message = "EAssert Condition is not true")
    {
      if (!condition) throw new EAssertException(message);
    }

    public static class Argument
    {
      internal static void IsNonEmptyString(string text, string argumentName = "Argument")
      {
        if (string.IsNullOrEmpty(text)) throw new ArgumentException($"{argumentName} cannot be empty or null string ({text}).");
      }

      internal static void IsNotNull(object? obj, string argumentName = "Argument")
      {
        if (obj == null) throw new ArgumentNullException(argumentName);
      }

      internal static void IsTrue(bool condition, string argumentName = "argument", string additionalMessage = "")
      {
        if (!condition) throw new ArgumentException($"Value of {argumentName} is invalid. {additionalMessage}".Trim());
      }
    }
  }
}
