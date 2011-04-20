import unittest
import datetime

from loggerglue.util.parse_timestamp import parse_timestamp


class TestParseTimestamp(unittest.TestCase):
    pairs = {
        '2003-10-11T22:14:15.003000Z':      datetime.datetime(2003, 10, 11, 22, 14, 15, 3000),
        '2003-10-11T22:14:15.003Z':         datetime.datetime(2003, 10, 11, 22, 14, 15, 3000),
        '2003-10-11T22:14:15Z':             datetime.datetime(2003, 10, 11, 22, 14, 15, 0),
        '2003-10-11T22:14:15.003000-07:00': datetime.datetime(2003, 10, 11, 15, 14, 15, 3000),
        '2003-10-11T22:14:15.003-07:00':    datetime.datetime(2003, 10, 11, 15, 14, 15, 3000),
        '2003-10-11T22:14:15-07:00':        datetime.datetime(2003, 10, 11, 15, 14, 15, 0),
    }

    longMessage = True

    def test_parse(self):
        for k, v in self.pairs.items():
            self.assertEqual(v, parse_timestamp(k), k)

if __name__ == '__main__':
    unittest.main()
