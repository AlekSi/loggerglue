# -*- coding: utf-8 -*-
"""
An rfc5424/rfc5425 syslog server implementation
Copyright © 2011 Evax Software <contact@evax.fr>
"""
import socket,os,sys
from datetime import datetime

from loggerglue.rfc5424 import DEFAULT_PRIVAL,SyslogEntry
from loggerglue.emitter import UNIXSyslogEmitter

class Logger(object):
    """
    Convenience class to log RFC5424 messages to the
    local syslog daemon (by default) or a remote
    syslog receiver.
    """

    def __init__(self, emitter=None, hostname=None, app_name=None, procid=None):
        """
        **Arguments**
            *emitter*
                Emitter object to send syslog messages, default to Unix socket /dev/log
                
            *hostname*
                Hostname to send with log messages, defaults to system hostname
                
            *app_name*
                Application name to send with log messages, defaults to application name
                
            *procid*
                Process ID to send with log messages, default to current process ID
        """
        if hostname is None:
            # Compute host name to submit to syslog
            hostname = socket.gethostname()

        if app_name is None:
            # Compute default app name from name of executable,
            # without extension.
            app_name = os.path.basename(sys.argv[0])
            (app_name, _, _) = app_name.partition(".") 

        if procid is None:
            procid = os.getpid()

        if emitter is None:
            emitter = UNIXSyslogEmitter()

        self.hostname = hostname
        self.app_name = app_name
        self.procid = procid
        self.emitter = emitter

    def log(self, msg=None, msgid=None, structured_data=None, prival=DEFAULT_PRIVAL, 
            timestamp=None):
        """
        Log a message. 

        Example:
        
           >>> logger.log("test", prival=LOG_DEBUG|LOG_MAIL)

        **Arguments**
            *msg*
                Human readable message to log
            *msgid*
                Message identifier
            *structured_data*
                Structured data to attach to log message
            *prival*
                Priority and facility of message (defaults to INFO|USER)
            *timestamp*
                UTC time of log message (default to current time)
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        msg = SyslogEntry(
                    prival=prival, timestamp=datetime.utcnow(), 
                    hostname=self.hostname, app_name=self.app_name, procid=self.procid, msgid=msgid,
                    structured_data=structured_data, 
                    msg=msg
            )

        self.emitter.emit(msg)

    def close(self):
        """
        Close connection to logger.
        """
        self.emitter.close()

