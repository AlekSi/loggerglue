# -*- coding: utf-8 -*-
"""
An rfc5424/rfc5425 syslog server implementation
Copyright © 2011 Evax Software <contact@evax.fr>
"""
import types, socket, ssl

# Default UDP port to send syslog messages
SYSLOG_DEFAULT_PORT             = 514

class SyslogEmitter(object):
    """
    Base class for syslog emitters. 
    
    A syslog emitter provides
    two methods, one to send messages and one to close the connection.
    All emitters are set up such that the connection is re-established
    once when a network issue happens. If the re-connection attempt fails,
    a socket exception is thrown.
    
    Derived classes have specific constructors describing the address
    to send messages to.
    """
    def close(self):
        """
        Closes the socket.
        """
        pass

    def emit(self, msg):
        """
        Emit a log record.
        """
        pass

class UDPSyslogEmitter(SyslogEmitter):
    """
    Syslog emitter through UDP.
    
    Sends syslog messages over UDP. As UDP is an unreliable protocol,
    use of this class is discouraged. The only use-case would be 
    sending messages to a syslog server that does not support TCP.
    """
    def __init__(self, address=('localhost', SYSLOG_DEFAULT_PORT)):
        """Create a Syslog emitter that sends messages through UDP.
        
        **Arguments**
        
            *address* 
                address to send messages to, as `(host,port)` tuple
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

class UNIXSyslogEmitter(SyslogEmitter):
    def __init__(self, address='/dev/log'):
        """Create a Syslog emitter that sends messages through a UNIX
        socket. This is useful for sending messages to a local
        syslog daemon.        
        
        **Arguments**
        
            *address*
                Address to send messages to, as string. Defaults to '/dev/log'.
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

class TCPSyslogEmitter(SyslogEmitter):
    """
    Syslog emitter that sends messages through a TCP socket. Optionally supports TLS.
    """
    def __init__(self, address=('localhost', SYSLOG_DEFAULT_PORT),\
        octet_based_framing=True, **ssl_args):
        """ 
        **Arguments**
            *address*
                Address to send messages to, specify this as `(host, port)` tuple.

            *octet_based_framing*
                Use RFC5425 octet-based framing instead of line-based framing. Use
                this when sending multiline messages.
                
            *keyfile*, *certfile*, *server_side*, *cert_reqs*, *ssl_version*, *ca_certs*, *ciphers*
                Arguments to pass through to :func:`ssl.wrap_socket`. Providing any of these arguments
                enables TLS.
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

