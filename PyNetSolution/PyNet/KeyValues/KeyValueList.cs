using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PyNet.KeyValues
{
  internal class KeyValueList<K, V> : List<KeyValue<K, V>> where K : class
  {
    public static KeyValueList<K, V> FromDictionary(Dictionary<K, V> dictionary)
    {
      KeyValueList<K, V> ret = new();

      foreach (var entry in dictionary)
      {
        ret.Add(entry.Key, entry.Value);
      }

      return ret;
    }

    public Dictionary<K, V> ToDictionary()
    {
      Dictionary<K, V> ret = new();

      foreach (var keyValue in this)
      {
        ret[keyValue.Key] = keyValue.Value;
      }

      return ret;
    }

    public void Add(K key, V value)
    {
      KeyValue<K, V> item = new KeyValue<K, V>(key, value);
      this.Add(item);
    }

    public V this[K key]
    {
      get
      {
        KeyValue<K, V> kv = this.FirstOrDefault(kv => kv.Key == key) ?? throw new KeyNotFoundException($"Key {key} not found.");
        V ret = kv.Value;
        return ret;
      }
      set
      {
        KeyValue<K, V> kv = this.FirstOrDefault(kv => kv.Key == key) ?? throw new KeyNotFoundException($"Key {key} not found.");
        kv.Value = value;
      }
    }
  }
}
