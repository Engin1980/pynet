using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PyNet
{
  public enum LogLevel
  {
    ALWAYS,
    CRITICAL,
    ERROR,
    WARNING,
    INFO,
    DEBUG,
    TRACE
  }

  public interface IWithLog
  {
    public delegate void LogHandler(object sender, LogLevel logLevel, string message, Exception? innerCauseIfAny = null);
    public event LogHandler? Log;
  }
}
