# -*- coding: utf-8 -*-
"""
A parser for the Syslog Protocol (RFC5424 - http://tools.ietf.org/search/rfc542)

Copyright © 2011 Evax Software <contact@evax.fr>
"""
from datetime import datetime, timedelta
from pyparsing import Word, Regex, Group, White, Combine, CharsNotIn, \
    ZeroOrMore, OneOrMore, QuotedString, Or, Optional, LineStart, LineEnd, \
    printables, ParseException
from loggerglue.util.MultiDict import OrderedMultiDict
from loggerglue.util.escape_value import escape_param_value, str_or_nil
from loggerglue.util.parse_timestamp import parse_timestamp

# Support SYSLOG_SyslogProtocol23Format which can send an empty APP-NAME.
SUPPORT_MISSING_VALUES = True

# from the RFCs ABNF description
nilvalue = Word("-")
digit = Regex("[0-9]{1}")
nonzero_digit = Regex("[1-9]{1}")
printusascii = printables
sp = White(" ", exact=1)
octet = Regex('[\x00-\xFF]')
utf_8_string = Regex('[\x00-\xFF]*')
BOM = '\xef\xbb\xbf'
bom = Regex(BOM)
msg_utf8 = bom + utf_8_string
msg_any = utf_8_string
msg = Combine(Or([msg_utf8, msg_any])).setResultsName('MSG')
sd_name = CharsNotIn('= ]"', 1, 32)
param_name = sd_name.setResultsName('SD_PARAM_NAME')
param_value = QuotedString(quoteChar='"', escChar='\\', multiline=True)
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
msgid = Or([nilvalue, CharsNotIn('= ]"', 1, 32)])
if SUPPORT_MISSING_VALUES:
    msgid = Optional(msgid)
msgid = msgid.setResultsName('MSGID')
procid = Or([nilvalue,CharsNotIn('= ]"', 1, 128)])
if SUPPORT_MISSING_VALUES:
    procid = Optional(procid)
procid = procid.setResultsName('PROCID')
app_name = Or([nilvalue, CharsNotIn('= ]"', 1, 48)])
if SUPPORT_MISSING_VALUES:
    app_name = Optional(app_name)
app_name= app_name.setResultsName('APP_NAME')
hostname = Or([nilvalue, CharsNotIn('= ]"', 1, 255)])
if SUPPORT_MISSING_VALUES:
    hostname = Optional(hostname)
hostname = hostname.setResultsName('HOSTNAME')
version = Regex('[1-9][0-9]{0,2}').setResultsName('VERSION')
prival = Regex("[0-9]{1,3}").setResultsName('PRIVAL')
pri = "<" + prival + ">"
header = pri + version + sp + timestamp + sp + hostname + sp + \
         app_name + sp + procid + sp + msgid
syslog_msg = LineStart() + header + structured_data + \
             Optional(sp+msg) + LineEnd()

# Default Prival for new SyslogEntry instances
from constants import LOG_INFO,LOG_USER
DEFAULT_PRIVAL = LOG_INFO|LOG_USER

class Params(object):
    def __init__(self, d):
        for k, v in d.items():
            setattr(self, k, v)

class SDElement(object):
    """
    An SD-ELEMENT consists of a name and parameter name-value pairs.
    """
    def __init__(self, sd_id, sd_params):
        """
        **arguments**
            *sd_id*
                SD-IDs are case-sensitive and uniquely identify the type and purpose
                of the SD-ELEMENT.
            
            *sd_params*
                Key/value pairs attached to this SD-ELEMENT. This can be any iterable
                that yields tuples, a dict or a :class:`~loggerglue.utils.multidict.OrderedMultiDict`
                (An SD-PARAM key may be repeated multiple times inside an SD-ELEMENT)
                
        **attributes**
            *id*
                SD-ID for this structured data element.
                
            *sd_params*
                Key/value pairs attached to this SD-ELEMENT, represented as 
                a multidict.
            
            *params*
                Key/value pairs attached to this SD-ELEMENT, represented as
                a class instance (for convenience, so that parameters can
                be addressed with `elmt.params.origin`). If there are multiple
                values for a key, the *last* element is returned.
                
        """
        self.id = sd_id
        self.sd_params = OrderedMultiDict(sd_params)
        self.params = Params(self.sd_params)
        
    def __str__(self):
        """Convert SDElement to formatted string"""
        rv = ['[', self.id]
        for (k,v) in self.sd_params.allitems():
            rv += [' ',k,'="',escape_param_value(v),'"']
        rv += [']']
        return ''.join(rv)

    @classmethod
    def parse(cls, parsed):
        sd = getattr(parsed, 'STRUCTURED_DATA', None)
        if sd is None or sd == '-':
            return None
        sd_id = parsed.STRUCTURED_DATA.SD_ID
        params = OrderedMultiDict()
        for i in parsed.STRUCTURED_DATA.SD_PARAMS:
            params[i.SD_PARAM.SD_PARAM_NAME] = \
                    i.SD_PARAM.SD_PARAM_VALUE.decode('utf-8')
        return StructuredData(sd_id, params)

class StructuredData(object):
    def __init__(self, elements):
        self.elements = elements
        
    def __str__(self):
        """Convert StructuredData to string"""
        return ''.join([str(e) for e in self.elements])

    @classmethod
    def parse(cls, parsed):
        sd = getattr(parsed, 'STRUCTURED_DATA', None)
        if sd is None or sd == '-':
            return None
        elements = []
        for se in parsed.SD_ELEMENTS:
            sd_id = se.SD_ID
            params = OrderedMultiDict()
            for i in se.SD_PARAMS:
                params[i.SD_PARAM.SD_PARAM_NAME] = \
                        i.SD_PARAM.SD_PARAM_VALUE.decode('utf-8')
            elements.append(SDElement(sd_id, params))
        return StructuredData(elements)

    @classmethod
    def from_str(cls, line):
        """Returns a StructuredData object from a string"""
        try:
            r = structured_data.parseString(line)
            return cls.parse(r)
        except Exception, e:
            print e
            import sys, traceback
            traceback.print_exc(file=sys.stdout)

            return None
    
class SyslogEntry(object):
    """
    A class representing a syslog entry.
    """
    def __init__(self, prival=DEFAULT_PRIVAL, version=1, timestamp=None, 
            hostname=None, app_name=None, procid=None, msgid=None,
            structured_data=None, msg=None):
        """
        **arguments/attributes**
            
            *prival*
                RFC5424 priority values are a combination of a priority and facility, for example `LOG_ALERT | LOG_DAEMON`.
                See :mod:`loggerglue.constants`.
            
            *version*
                Version of syslog entry. There is usually no need to change this.
            
            *timestamp*
                Timestamp (as a datetime object).
            
            *hostname*
                The HOSTNAME field SHOULD contain the hostname and the domain name of the originator.
            
            *app_name*
                The APP-NAME field SHOULD identify the device or application that
                originated the message.  It is a string without further semantics.
                It is intended for filtering messages on a relay or collector.
            
            *procid*
                PROCID is a value that is included in the message, having no
                interoperable meaning, except that a change in the value indicates
                there has been a discontinuity in syslog reporting. 
            
            *msgid*
                The MSGID SHOULD identify the type of message.
            
            *structured_data*
                STRUCTURED-DATA provides a mechanism to express information in a well
                defined, easily parseable and interpretable data format.
            
            *msg*
                The MSG part contains a free-form message that provides information
                about the event.

        """
        self.prival = prival
        self.version = version
        self.timestamp = timestamp
        self.hostname = hostname
        self.app_name = app_name
        self.procid = procid
        self.msgid = msgid
        if structured_data is not None and not isinstance(structured_data, StructuredData):
            structured_data = StructuredData(structured_data)
        self.structured_data = structured_data
        self.msg = msg
    
    @classmethod
    def parse(cls, parsed):
        ts = parse_timestamp(parsed.TIMESTAMP)
        if ts is None:
            # If no timestamp provided, fill in current UTC date and time
            timestamp = datetime.utcnow()
        else:
            timestamp = ts
        attr = {}
        for i in ('prival', 'version', 'hostname', 'app_name',
                  'procid', 'msgid'):
            I = i.upper()
            v = getattr(parsed, I, '-')
            if v in ["", "-"]:
                v = None
            else:
                v = v.decode('utf-8')
            attr[i] = v
        m = getattr(parsed, 'MSG', None)
        if m is not None:
            if m.startswith(BOM):
                msg = m[3:].decode('utf-8')
            else:
                msg = unicode(m)
        else:
            msg = None
        version = int(attr['version'])
        prival = int(attr['prival'])
        structured_data = StructuredData.parse(parsed)
        return cls(
            prival=prival, version=version, timestamp=timestamp, 
            hostname=attr['hostname'], app_name=attr['app_name'], procid=attr['procid'], msgid=attr['msgid'],
            structured_data=structured_data, msg=msg
        )
        
    def __str__(self):
        """Convert SyslogEntry to string"""
        rv = ['<', str(self.prival), '>', str(self.version), ' ']
        if self.timestamp is None:
            rv.append('-')
        else:
            rv.append(self.timestamp.strftime("%Y-%m-%dT%H:%M:%S.%fZ"))
        rv += [' ',
               str_or_nil(self.hostname), ' ', str_or_nil(self.app_name), ' ', str_or_nil(self.procid), ' ',
               str_or_nil(self.msgid),    ' ', str_or_nil(self.structured_data)]
        if self.msg is not None:
            rv += [' ']
            if type(self.msg) is unicode:
                rv += [BOM, self.msg.encode('utf-8')]
            else:
                rv += [self.msg]
        return ''.join(rv)

    @classmethod
    def from_line(cls, line):
        """Returns a parsed SyslogEntry object from a syslog `line`."""
        try:
            r = syslog_msg.parseString(line.strip())
            return cls.parse(r)
        except Exception, e:
            print e
            import sys, traceback
            traceback.print_exc(file=sys.stdout)

            return None

