using PyNet.EAsserting;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PyNet.KeyValues
{
  internal class KeyValue<K, V> where K : class
  {
    private K _Key;

    public KeyValue(K key, V value)
    {
      Key = key;
      Value = value;
    }

    public K Key { get => _Key; set => _Key = value.Tap(q => EAssert.IsNotNull(q)); }
    public V Value { get; set; }


  }
}
