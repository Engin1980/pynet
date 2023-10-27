using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PyNet.EAsserting
{
  internal class EAssertException : Exception
  {
    public EAssertException(string message) : base(message) { }
  }
}
