using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection.Metadata.Ecma335;
using System.Text;
using System.Threading.Tasks;

namespace PyNet.Testing
{
  public class TestFullBody
  {
    public int Int { get; set; } = 8;
    public double Double { get; set; } = -20.203;
    public float Float { get; set; } = -1212.423f;
    public string String { get; set; } = "some random text";
    public string? Null { get; set; } = null;
    public byte[] ByteArray { get; set; } = new byte[] { 0, 1, 2, 3, 4, 5, 6 };
  }
}
