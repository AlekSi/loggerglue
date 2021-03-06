=================
 Getting Started
=================

.. toctree::
   :maxdepth: 2

loggerglue is intended to be a general purpose glue layer for the syslog protocol as decribed in RFC5424_ and RFC5425_.

This package includes:

    * a pyparsing parser for rfc5424
    * a wrapper class for rfc5424 syslog entries
    * a SyslogServer class supporting TLS (rcf5425)
    * classes for constructing and emitting rfc5424 syslog entries

To make use of RFC5424 functionality such as sending structured data with messages, you need a recent syslog
that supports the protocol, such as rsyslog_.

Examples
========

Client example
------------------------

Log a simple message with structured data to the local syslog daemon:

::

    >>> from loggerglue import logger
    >>> from loggerglue.rfc5424 import SDElement
    >>> from loggerglue.constants import *
    >>> l = logger.Logger()
    >>> l.log(prival=LOG_INFO|LOG_USER,
              msg="Test message",
              structured_data=[
                  SDElement("origin",
                      [("software","test script"), ("swVersion","0.0.1")])
              ])


A trivial server example
------------------------

A simple TLS enabled server can be built as follows:

::

    from loggerglue.server import SyslogServer, SyslogHandler

    class SimpleHandler(SyslogHandler):
        def handle_entry(self, entry):
            print 'On %s from %s: %s' % \
                    (entry.timestamp, entry.hostname, entry.msg)

    s = SyslogServer(('127.0.0.1', 6514), SimpleHandler,
                    keyfile='loggerglue-key.pem',
                    certfile='loggerglue-cert.pem')
    s.serve_forever()

Here's an example rsyslog configuration:

::

    $IncludeConfig /etc/rsyslog.d/*.conf

    $DefaultNetstreamDriverCAFile /path/to/loggerglue-ca-cert.pem
    $DefaultNetstreamDriver gtls
    $ActionSendStreamDriverMode 1
    $ActionSendStreamDriverAuthMode anon

    *.* @@(o)localhost:6514;RSYSLOG_SyslogProtocol23Format

A more advanced server example
------------------------------

In this exemple we index the log data as it comes using Whoosh.

::

    from loggerglue.server import SyslogServer, SyslogHandler
    from whoosh import index
    from whoosh.fields import *
    import os.path

    schema = Schema(prio=ID(stored=True),
                    timestamp=DATETIME(stored=True),
                    hostname=ID(stored=True),
                    app_name=ID(stored=True),
                    procid=ID(stored=True),
                    msgid=ID(stored=True),
                    msg=TEXT(stored=True)
                    )

    if os.path.exists('indexdir'):
        ix = index.open_dir('indexdir')
    else:
        os.mkdir('indexdir')
        ix = index.create_in('indexdir', schema)

    class SimpleHandler(SyslogHandler):
        def handle_entry(self, entry):
            writer = ix.writer()
            writer.add_document(prio=entry.prival,
                                timestamp=entry.timestamp,
                                hostname=entry.hostname,
                                app_name=entry.app_name,
                                procid=entry.procid,
                                msgid=entry.msgid,
                                msg=entry.msg)
            writer.commit()

    s = SyslogServer(('127.0.0.1', 6514), SimpleHandler,
                    keyfile='loggerglue-key.pem',
                    certfile='loggerglue-cert.pem')
    s.serve_forever()

And now a small search tool:

::

    from whoosh import index
    from whoosh.qparser import QueryParser

    import sys
    if len(sys.argv) == 1:
        print 'usage: %s <search terms>' % sys.argv[0]
        sys.exit(1)

    ix = index.open_dir('indexdir')
    searcher = ix.searcher()
    query = QueryParser('msg').parse(' '.join(sys.argv[1:]))
    results = searcher.search(query)
    print '%d results\n' % len(results)
    for r in results:
        print '%s\n' % str(r)
    searcher.close()



.. _RFC5424: http://tools.ietf.org/html/rfc5424
.. _RFC5425: http://tools.ietf.org/html/rfc5425
.. _rsyslog: http://www.rsyslog.com/

