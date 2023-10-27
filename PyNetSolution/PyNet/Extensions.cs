using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PyNet
{
  public static class Extensions
  {
    public static T Tap<T>(this T me, Action<T> action)
    {
      action.Invoke(me);
      return me;
    }
  }
}
