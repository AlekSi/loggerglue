# -*- coding: utf-8 -*-
"""
An rfc5424/rfc5425 syslog server implementation
Copyright © 2011 Evax Software <contact@evax.fr>
"""
import ssl
import SocketServer
from loggerglue.rfc5424 import SyslogEntry

class SyslogHandler(SocketServer.BaseRequestHandler):

    def setup(self):
        if not self.server.use_tls:
            self.connection = self.request.makefile()

    def finish(self):
        if not self.server.use_tls:
            self.connection.close()

    def handle(self):
        if self.server.use_tls:
            return self.handle_tls()
        while not self.connection.closed:
            line = self.connection.readline()
            syslog_entry = SyslogEntry.from_line(line)
            if syslog_entry:
                self.handle_entry(syslog_entry)
            else:
                self.handle_error(line)

    def handle_tls(self):
        buf = ''
        while True:
            r = self.request.recv(1)
            if r != ' ':
                buf += r
            else:
                try:
                    msg_len = int(buf)
                except:
                    # Protocol error
                    return
                buf = ''
                for i in xrange(msg_len):
                    buf += self.request.recv(1)
                syslog_entry = SyslogEntry.from_line(buf)
                buf = ''
                if syslog_entry is None:
                    self.handle_error(buf)
                self.handle_entry(syslog_entry)

    def handle_entry(self, syslog_entry):
        raise NotImplemented('Subclasses must implement this method')

    def handle_error(self, data):
        """Implementing this method is optional."""
        pass

class SyslogServer(SocketServer.TCPServer, SocketServer.ThreadingMixIn):
    allow_reuse_address = True

    _allowed_ssl_args = ('keyfile', 'certfile', 'cert_reqs', 'ssl_version',
                         'ca_certs', 'suppress_ragged_eofs')

    def __init__(self, server_address, RequestHandlerClass,
                 bind_and_activate=True,
                 **ssl_args):
        self.use_tls = False
        if ssl_args:
            for arg in ssl_args:
                if arg not in self._allowed_ssl_args:
                    raise TypeError('unexpected keyword argument: %s' %arg)
            self.ssl_args = ssl_args
            self.use_tls = True
        SocketServer.TCPServer.__init__(self, server_address,
                                        RequestHandlerClass,
                                        bind_and_activate)

    def get_request(self):
        conn, addr = self.socket.accept()
        if self.use_tls:
            conn = ssl.wrap_socket(conn, server_side=True,
                                   **self.ssl_args)
        return (conn, addr)

