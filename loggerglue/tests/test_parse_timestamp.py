import unittest
import datetime

from loggerglue.util.parse_timestamp import parse_timestamp


class TestParseTimestamp(unittest.TestCase):
    pairs = {
        '2003-10-11T12:14:15.003000Z':      datetime.datetime(2003, 10, 11, 12, 14, 15, 3000),
        '2003-10-11T12:14:15.003Z':         datetime.datetime(2003, 10, 11, 12, 14, 15, 3000),
        '2003-10-11T12:14:15Z':             datetime.datetime(2003, 10, 11, 12, 14, 15, 0),

        '2003-10-11T12:14:15.003000+04:00': datetime.datetime(2003, 10, 11,  8, 14, 15, 3000),
        '2003-10-11T12:14:15.003+04:00':    datetime.datetime(2003, 10, 11,  8, 14, 15, 3000),
        '2003-10-11T12:14:15+04:00':        datetime.datetime(2003, 10, 11,  8, 14, 15, 0),

        # Pacific/Kiritimati
        '2003-10-11T12:14:15.003000+14:00': datetime.datetime(2003, 10, 10, 22, 14, 15, 3000),
        '2003-10-11T12:14:15.003+14:00':    datetime.datetime(2003, 10, 10, 22, 14, 15, 3000),
        '2003-10-11T12:14:15+14:00':        datetime.datetime(2003, 10, 10, 22, 14, 15, 0),

        '2003-10-11T12:14:15.003000-04:00': datetime.datetime(2003, 10, 11, 16, 14, 15, 3000),
        '2003-10-11T12:14:15.003-04:00':    datetime.datetime(2003, 10, 11, 16, 14, 15, 3000),
        '2003-10-11T12:14:15-04:00':        datetime.datetime(2003, 10, 11, 16, 14, 15, 0),

        '2003-10-11T12:14:15.003000-12:00': datetime.datetime(2003, 10, 12,  0, 14, 15, 3000),
        '2003-10-11T12:14:15.003-12:00':    datetime.datetime(2003, 10, 12,  0, 14, 15, 3000),
        '2003-10-11T12:14:15-12:00':        datetime.datetime(2003, 10, 12,  0, 14, 15, 0),
    }

    longMessage = True

    def test_parse(self):
        for k, v in self.pairs.items():
            self.assertEqual(v, parse_timestamp(k), k)

if __name__ == '__main__':
    unittest.main()
