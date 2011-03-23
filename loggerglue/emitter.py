# -*- coding: utf-8 -*-
"""
An rfc5424/rfc5425 syslog server implementation
Copyright © 2011 Evax Software <contact@evax.fr>
"""
import types, socket, ssl

# Default UDP port to send syslog messages
SYSLOG_DEFAULT_PORT             = 514

class SyslogEmitter(object):
    def close(self):
        """
        Closes the socket.
        """
        pass

    def emit(self, msg):
        """
        Emit a record.
        """
        pass

class UDPSyslogEmitter(SyslogEmitter):
    def __init__(self, address=('localhost', SYSLOG_DEFAULT_PORT)):
        """Create a Syslog emitter that sends messages through UDP.
        
        Keyword arguments:
        address -- address to send messages to, as (host,port) tuple
        """
        self.address = address
        self._connect(address)
        
    def _connect(self, address):
        """(Re-)connect to socket"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def close(self):
        """
        Closes the socket.
        """
        pass

    def emit(self, msg):
        """
        Emit a record.
        """
        self.socket.sendto(str(msg), self.address)

class UNIXSyslogEmitter(object):
    def __init__(self, address='/dev/log'):
        """Create a Syslog emitter that sends messages through a UNIX
        socket.
        
        Keyword arguments:
        address -- address to send messages to, as string. Defaults to '/dev/log'.
        """
        self.address = address
        self._connect(address)
        
    def _connect(self, address):
        """(Re-)connect to socket"""
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        try:
            self.socket.connect(address)
        except socket.error:
            self.socket.close()
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(address)

    def close(self):
        """
        Closes the socket.
        """
        self.socket.close()

    def emit(self, msg):
        """
        Emit a record.
        """
        try:
            self.socket.send(str(msg)+'\000')
        except socket.error:
            self._connect(self.address)
            self.socket.send(str(msg)+'\000')

class TCPSyslogEmitter(object):
    def __init__(self, address=('localhost', SYSLOG_DEFAULT_PORT),\
        octet_based_framing=True, **ssl_args):
        """Create a Syslog emitter that sends messages through a TCP
        socket.
        
        Keyword arguments:
        address -- address to send messages to, as (host, port) tuple.
        use_tls -- Use TLS for encrypting the connection
        ssl_args -- Arguments to pass to ssl.wrap_socket
        """
        self.address = address
        self.octet_based_framing = octet_based_framing
        self.ssl_args = ssl_args
        self._connect(address, ssl_args)
        
    def _connect(self, address, ssl_args):
        """(Re-)connect to socket"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(address)
        if ssl_args:
            self.socket = ssl.wrap_socket(self.socket, server_side=False,
                                   **ssl_args)

    def close(self):
        """
        Closes the socket.
        """
        try:
            self.socket.close()
        except socket.error:
            pass
        
    def _send(self, msg):
        msg = str(msg)
        if self.octet_based_framing:
            self.socket.send("%i %s" % (len(msg), msg))
        else:
            self.socket.send(msg + '\n')

    def emit(self, msg):
        """
        Emit a record.
        """
        try:
            self._send(msg)
        except socket.error:
            self._connect(self.address, self.ssl_args)
            self._send(msg)

