# -*- coding: utf-8 -*-
"""
A parser for the Syslog Protocol
(RFC5424 - http://tools.ietf.org/search/rfc5424)
Copyright © 2011 Evax Software <contact@evax.fr>
"""
from datetime import datetime, timedelta
from pyparsing import *

# from the RFCs ABNF description
nilvalue = Word("-")
digit = Regex("[0-9]{1}")
nonzero_digit = Regex("[1-9]{1}")
printusascii = printables
sp = White(" ")
octet = Regex('[\x00-\xFF]')
utf_8_string = Regex('[\x00-\xFF]*')
BOM = '\xef\xbb\xbf'
bom = Regex(BOM)
msg_utf8 = bom + utf_8_string
msg_any = utf_8_string
msg = Combine(Or([msg_utf8, msg_any])).setResultsName('MSG')
sd_name = CharsNotIn('= ]"', 1, 32)
param_name = sd_name.setResultsName('SD_PARAM_NAME')
param_value = QuotedString(quoteChar='"', escChar='\\')
param_value = param_value.setResultsName('SD_PARAM_VALUE')
sd_id = sd_name.setResultsName('SD_ID')
sd_param = Group(param_name + Regex('=') + param_value)
sd_params = Group(ZeroOrMore(Group(sp+sd_param.setResultsName('SD_PARAM'))))
sd_element = Group('['+sd_id+sd_params.setResultsName('SD_PARAMS')+']')
sd_element = sd_element.setResultsName('SD_ELEMENT')
sd_elements = Group(OneOrMore(sd_element))
structured_data = Or([nilvalue, sd_elements.setResultsName('SD_ELEMENTS')])
structured_data = structured_data.setResultsName('STRUCTURED_DATA')
time_hour = Regex('0[0-9]|1[0-9]|2[0-3]')
time_minute = Regex('[0-5][0-9]')
time_second = time_minute
time_secfrac = Regex('\.[0-9]{1,6}')
time_numoffset = Or([Regex('\+'), Regex('-')]) + \
                 time_hour + ':' + time_minute
time_offset = Or([Regex('Z'), time_numoffset])
partial_time = time_hour + ':' + time_minute + ':' + time_second + \
               Optional(time_secfrac)
full_time = partial_time + time_offset
date_mday = Regex('[0-9]{2}')
date_month = Regex('0[1-9]|1[0-2]')
date_fullyear = Regex('[0-9]{4}')
full_date = date_fullyear + '-' + date_month + '-' + date_mday
timestamp = Combine(Or([nilvalue, full_date + 'T' + full_time]))
timestamp = timestamp.setResultsName('TIMESTAMP')
msgid = Or([nilvalue, CharsNotIn('= ]"', 1, 32)]).setResultsName('MSGID')
procid = Or([nilvalue,CharsNotIn('= ]"', 1, 128)]).setResultsName('PROCID')
app_name = Or([nilvalue, CharsNotIn('= ]"', 1, 48)])
app_name= app_name.setResultsName('APP_NAME')
hostname = Or([nilvalue, CharsNotIn('= ]"', 1, 255)])
hostname = hostname.setResultsName('HOSTNAME')
version = Regex('[1-9][0-9]{0,2}').setResultsName('VERSION')
prival = Regex("[0-9]{1,3}").setResultsName('PRIVAL')
pri = "<" + prival + ">"
header = pri + version + sp + timestamp + sp + hostname + sp + \
         app_name + sp + procid + sp + msgid
syslog_msg = LineStart() + header + structured_data + \
             Optional(sp+msg) + LineEnd()

class Params(object):
    def __init__(self, d):
        for k, v in d.items():
            setattr(self, k, v)

class SDElement(object):
    def __init__(self, sd_id, sd_params):
        self.id = sd_id
        self.sd_params = sd_params
        self.params = Params(sd_params)

    @classmethod
    def parse(cls, parsed):
        sd = getattr(parsed, 'STRUCTURED_DATA', None)
        if sd is None or sd == '-':
            return None
        sd_id = parsed.STRUCTURED_DATA.SD_ID
        params = {}
        for i in parsed.STRUCTURED_DATA.SD_PARAMS:
            params[i.SD_PARAM.SD_PARAM_NAME] = \
                    i.SD_PARAM.SD_PARAM_VALUE.decode('utf-8')
        return StructuredData(sd_id, params)

class StructuredData(object):
    def __init__(self, elements):
        self.elements = elements

    @classmethod
    def parse(cls, parsed):
        sd = getattr(parsed, 'STRUCTURED_DATA', None)
        if sd is None or sd == '-':
            return None
        elements = []
        for se in parsed.SD_ELEMENTS:
            sd_id = se.SD_ID
            params = {}
            for i in se.SD_PARAMS:
                params[i.SD_PARAM.SD_PARAM_NAME] = \
                        i.SD_PARAM.SD_PARAM_VALUE.decode('utf-8')
            elements.append(SDElement(sd_id, params))
        return StructuredData(elements)

class SyslogEntry(object):
    """A class representing a syslog entry."""
    def __init__(self, parsed):
        self._parsed = parsed
        ts = parsed.TIMESTAMP
        if ts == '-':
            self.timestamp = datetime.now()
        elif ts[-1] == 'Z':
            self.timestamp = datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            self.timestamp = datetime.strptime(ts[:-6],
                                               "%Y-%m-%dT%H:%M:%S.%f")
            hours = int(ts[-5:-3])
            mins = int(ts[-2:])
            sign = ts[-6] == '-' and -1 or 1
            self.timestamp += timedelta(sign*(hours*3600+mins*60))
        for i in ('prival', 'version', 'hostname', 'app_name',
                  'procid', 'msgid'):
            I = i.upper()
            v = getattr(parsed, I, None)
            if v is not None:
                v = v.decode('utf-8')
            setattr(self, i, v)
        m = getattr(parsed, 'MSG', None)
        if m is not None:
            if m.startswith(BOM):
                self.msg = m[3:].decode('utf-8')
            else:
                self.msg = unicode(m)
        else:
            self.msg = None
        self.structured_data = StructuredData.parse(parsed)

    @classmethod
    def from_line(cls, line):
        """Returns a SyslogEntry object from a syslog line."""
        try:
            r = syslog_msg.parseString(line.strip())
            return SyslogEntry(r)
        except Exception, e:
            print e
            import sys, traceback
            traceback.print_exc(file=sys.stdout)

            return None

