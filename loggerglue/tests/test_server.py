"""
Tests for both the Syslog server and emitter.
"""
import unittest
from loggerglue.emitter import TCPSyslogEmitter
from loggerglue.server import SyslogServer,SyslogHandler
from loggerglue.rfc5424 import StructuredData, SyslogEntry, SDElement
from datetime import datetime
import socket, os, time, threading
from tempfile import NamedTemporaryFile

def create_test_entry(proto):
    hostname = "test.example.com"
    app_name = "app_name"
    y = SyslogEntry(
            prival=165, timestamp=datetime.utcnow(), 
            hostname=hostname, app_name=app_name, procid=os.getpid(), msgid='ID47',
            structured_data=[SDElement('exampleSDID@32473', 
                [('iut','3'),
                ('eventSource','Application'),
                ('eventID','1011'),
                ('eventID','1012')]
                )], 
            msg='An application event log entry through '+proto+'...'
    )
    return y

class Handler(SyslogHandler):
    def handle_entry(self, syslog_entry):
        self.server.entry = syslog_entry

def syslog_server_thread(serv):
    """Handle one request"""
    serv.handle_request()

# SSL test certificate/key
key_data = """
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQC+K1APSGZB9BsZJwUa6L1qIa8eIxxJtZnYknMsf34ZnJzpg8vw
LjjeuFB4OAmIudY7iHDkBIRrOOUemtWf5zOjZIZUZBWXtH5dpoNSkdcU1UnVYFyV
GkS05Sta2sDL0M1Vo0HQTzj2D7OGxQkvoza9/oeLmH5WyFqTWfMySP0lYQIDAQAB
AoGAeHnaI4R7fAcY78tfmZefAFDMr2wQ7MWG7MSDAMrYaYNliS69EbFGyBq+qBrg
N2V8SoT6+AnAlmkaBlSTR9ViSWbA4TZYZt7wrcu/ld20GE4k3K2zua6Pl4bgxG2h
QzmpDQoID7eKPfZiIUch7sCjzxqv4nJNmE3gO+MicX6cf0ECQQDdt+YXJN7Tb3YS
N35cMGA/ZEi7eYYlIux3wEDTm4Mm93EmE1S+BU2J/fm7P5nihctV4ebgwUicE/nG
ahVXEyKZAkEA25Kg49VbV09IrS3iP1gaY3DDWaenfJNWwDlUOymk3KPzc/gbiuza
S50sWZJ//Wi3bTIrJPwcGtkHLAvAUjseCQJAMqbcjdUCgtMn6il7WJxEoLbMVugA
WWONGh51sOIKKFDHLKel6HNVr3yyHLD++t0OAuTE1fvSFrYJjeaWUXoxoQJAPWU5
kZs16CrmIm5jBd1Hu6hrJyWG4oF8T1F4aPaS/5LkXvfwE594xo3TOdSJ7zyZlXHi
uHu6DBPFOp6qjxOyqQJBAK8xkuYCCbZYEiiCt21xS+D7emOxQZ0eZf938u3A3/7p
FYoTjD5y9gK7utBjaQYtR/dIK5HnRQTycxvmdW4o2dQ=
-----END RSA PRIVATE KEY-----
"""

cert_data = """
-----BEGIN CERTIFICATE-----
MIIDEzCCAnwCCQDq8BfSOBmMxjANBgkqhkiG9w0BAQUFADCBzTELMAkGA1UEBhMC
WFgxKjAoBgNVBAgTIVRoZXJlIGlzIG5vIHN1Y2ggdGhpbmcgb3V0c2lkZSBVUzET
MBEGA1UEBxMKRXZlcnl3aGVyZTEOMAwGA1UEChMFT0NPU0ExPDA6BgNVBAsTM09m
ZmljZSBmb3IgQ29tcGxpY2F0aW9uIG9mIE90aGVyd2lzZSBTaW1wbGUgQWZmYWly
czERMA8GA1UEAxMIcGhvc3Bob3IxHDAaBgkqhkiG9w0BCQEWDXJvb3RAcGhvc3Bo
b3IwHhcNMDgwNTMwMTA0NzQ1WhcNMDgwNjI5MTA0NzQ1WjCBzTELMAkGA1UEBhMC
WFgxKjAoBgNVBAgTIVRoZXJlIGlzIG5vIHN1Y2ggdGhpbmcgb3V0c2lkZSBVUzET
MBEGA1UEBxMKRXZlcnl3aGVyZTEOMAwGA1UEChMFT0NPU0ExPDA6BgNVBAsTM09m
ZmljZSBmb3IgQ29tcGxpY2F0aW9uIG9mIE90aGVyd2lzZSBTaW1wbGUgQWZmYWly
czERMA8GA1UEAxMIcGhvc3Bob3IxHDAaBgkqhkiG9w0BCQEWDXJvb3RAcGhvc3Bo
b3IwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAL4rUA9IZkH0GxknBRrovWoh
rx4jHEm1mdiScyx/fhmcnOmDy/AuON64UHg4CYi51juIcOQEhGs45R6a1Z/nM6Nk
hlRkFZe0fl2mg1KR1xTVSdVgXJUaRLTlK1rawMvQzVWjQdBPOPYPs4bFCS+jNr3+
h4uYflbIWpNZ8zJI/SVhAgMBAAEwDQYJKoZIhvcNAQEFBQADgYEAZHouYp7yKH0o
b0Z8KRGxu408vAjGFg9nXS0BhK3N+zNy574f3/NFHlNR8nNMcROEKHH6NmXpYnuQ
sRtTT/S7b2ctasdeZHH8V/DNvVRRe55gB3z3AeG+OLvOgRHROgpNYStttYJrarEp
fALEMmG3RMNk2r0FlksHlCQV7L9jp8M=
-----END CERTIFICATE-----
"""


class TestServer(unittest.TestCase):

    def test_tcp(self):
        address = ('127.0.0.1', 5514)
        
        serv = SyslogServer(address, Handler)
        serv.entry = None
        
        thr = threading.Thread(
            target=syslog_server_thread, args=(serv,))
        thr.start()
        tm = TCPSyslogEmitter(address, octet_based_framing=False)
        y = create_test_entry('TCP')
        tm.emit(y)
        tm.close()
        thr.join()
        serv.socket.close()
        
        self.assertEqual(serv.entry.msg, "An application event log entry through TCP...")

    def test_tcps(self):
        address = ('127.0.0.1', 5515)
        
        keyfile = NamedTemporaryFile(delete=False)
        keyfile.write(key_data)
        keyfile.close()
        certfile = NamedTemporaryFile(delete=False)
        certfile.write(cert_data)
        certfile.close()
        serv = SyslogServer(address, Handler, 
            keyfile=keyfile.name,
            certfile=certfile.name)
        serv.entry = None

        thr = threading.Thread(
            target=syslog_server_thread, args=(serv,))
        thr.start()
        tm = TCPSyslogEmitter(address, octet_based_framing=True,
                keyfile=None)
        y = create_test_entry('TCPS')
        tm.emit(y)
        tm.close()
        thr.join()

        serv.socket.close()
        
        os.unlink(keyfile.name)
        os.unlink(certfile.name)

        self.assertEqual(serv.entry.msg, "An application event log entry through TCPS...")

if __name__ == '__main__':
    unittest.main()

