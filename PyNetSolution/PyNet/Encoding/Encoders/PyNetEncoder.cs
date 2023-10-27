using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PyNet.Encoding
{
  internal class PyNetEncoder<T>
  {
    public PyNetEncoder(Func<object?, bool> acceptsValue, Func<string, bool> acceptsTypeId,
      Func<T, string> toTypeId, Func<T, byte[]> toData,
      Func<string, int> toByteLen,
      Func<byte[], T> toValue)
    {
      AcceptsValue = acceptsValue;
      AcceptsTypeId = acceptsTypeId;
      ToTypeId = toTypeId;
      ToData = toData;
      ToByteLen = toByteLen;
      ToValue = toValue;
    }

    public Func<object?, bool> AcceptsValue { get; private set; }
    public Func<string, bool> AcceptsTypeId { get; private set; }
    public Func<T, string> ToTypeId { get; private set; }
    public Func<T, byte[]> ToData { get; private set; }
    public Func<byte[], T> ToValue { get; private set; }
    public Func<string, int> ToByteLen { get; private set; }
  }
}
