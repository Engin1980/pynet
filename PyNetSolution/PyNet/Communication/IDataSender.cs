using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PyNet.Communication
{
  public interface IDataSender
  {
    public void Send(byte[] data);
  }
}
