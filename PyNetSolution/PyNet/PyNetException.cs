using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PyNet
{
  public class PyNetException : ApplicationException
  {
    public PyNetException(string message) : base(message) { }
    public PyNetException(string message, Exception cause) : base(message, cause) { }
  }
}
