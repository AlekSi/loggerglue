import unittest
from loggerglue.rfc5424 import *

valids = (
        """<34>1 2003-10-11T22:14:15.003Z mymachine.example.com su - ID47 - \xef\xbb\xbf'su root' failed for lonvick on /dev/pts/8""",
        """<165>1 2003-08-24T05:14:15.000003-07:00 192.0.2.1 myproc 8710 - - %% It's time to make the do-nuts.""",
        """<165>1 2003-10-11T22:14:15.003Z mymachine.example.com evntslog - ID47 [exampleSDID@32473 iut="3" eventSource="Application" eventID="1011"] \xef\xbb\xbfAn application event log entry...""",
        """<165>1 2003-10-11T22:14:15.003Z mymachine.example.com evntslog - ID47 [exampleSDID@32473 iut="3" eventSource="Application" eventID="1011"][examplePriority@32473 class="high"]""",
        )

invalids = (
        """This is obviously invalid.""",
        )

class TestABNF(unittest.TestCase):

    def test_valids(self):
        for v in valids:
            r = syslog_msg.parseString(v)

    def test_invalids(self):
        for i in invalids:
            self.assertRaises(ParseException, syslog_msg.parseString, i)

    def test_details(self):
        r = syslog_msg.parseString(valids[0])
        self.assertEqual(r.PRIVAL, '34')
        self.assertEqual(r.VERSION, '1')
        self.assertEqual(r.TIMESTAMP, '2003-10-11T22:14:15.003Z')
        self.assertEqual(r.HOSTNAME, 'mymachine.example.com')
        self.assertEqual(r.APP_NAME, 'su')
        self.assertEqual(r.PROCID, '-')
        self.assertEqual(r.STRUCTURED_DATA, '-')
        self.assertEqual(r.MSG,
                "\xef\xbb\xbf'su root' failed for lonvick on /dev/pts/8")
        r = syslog_msg.parseString(valids[2])
        self.assertTrue(hasattr(r.STRUCTURED_DATA, 'SD_ID'))
        r = syslog_msg.parseString(valids[3])
        self.assertEqual(len(r.SD_ELEMENTS), 2)
        self.assertEqual(len(r.SD_ELEMENTS[0].SD_PARAMS), 3)
        self.assertEqual(len(r.SD_ELEMENTS[1].SD_PARAMS), 1)

class TestSyslogEntry(unittest.TestCase):

    def test_class(self):
        for v in valids:
            se = SyslogEntry.from_line(v)
            self.assertTrue(se is not None)

    def test_details(self):
        se = SyslogEntry.from_line(valids[0])
        self.assertEqual(se.msg,
                """'su root' failed for lonvick on /dev/pts/8""")
        self.assertEqual(se.timestamp.year, 2003)
        self.assertEqual(se.hostname, 'mymachine.example.com')
        self.assertEqual(se.msgid, 'ID47')
        se = SyslogEntry.from_line(valids[3])
        self.assertEqual(len(se.structured_data.elements), 2)
        self.assertEqual(len(se.structured_data.elements[0].sd_params), 3)
        self.assertEqual(len(se.structured_data.elements[1].sd_params), 1)

if __name__ == '__main__':
    unittest.main()

