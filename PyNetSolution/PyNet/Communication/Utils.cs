using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;

namespace PyNet.Communication
{
  public class Utils
  {
    public static IPAddress ConvertToIp(string ip)
    {
      IPAddress ret;

      string lip = ip switch
      {
        "localhost" => "127.0.0.1",
        _ => ip
      };

      try
      {
        ret = IPAddress.Parse(lip);
      }
      catch (Exception ex)
      {
        throw new PyNetException($"Failed to parse '{ip}' to IP address.", ex);
      }
      return ret;
    }
  }
}
