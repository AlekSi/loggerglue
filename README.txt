loggerglue - Syslog protocol (rfc5424 and rfc5425) utilities
============================================================

loggerglue is intended to be a general purpose glue layer for the
syslog protocol as decribed in rfc5424__ and rfc5425__.

__ http://tools.ietf.org/search/rfc5424
__ http://tools.ietf.org/search/rfc5425

This package includes:

* a pyparsing parser for rfc5424
* a wrapper class for rfc5424 syslog entries
* a SyslogServer class supporting TLS (rcf5425)

A trivial example
-----------------

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

Here's an example rsyslog__ configuration:

__ http://www.rsyslog.com

::

    $IncludeConfig /etc/rsyslog.d/*.conf

    $DefaultNetstreamDriverCAFile /path/to/loggerglue-ca-cert.pem
    $DefaultNetstreamDriver gtls
    $ActionSendStreamDriverMode 1
    $ActionSendStreamDriverAuthMode anon

    *.* @@(o)localhost:6514;RSYSLOG_SyslogProtocol23Format

A more advanced example
-----------------------

In this exemple we index the log data as it comes using Woosh__.

__ https://bitbucket.org/mchaput/whoosh/wiki/Home

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

