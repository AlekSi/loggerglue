from datetime import datetime, timedelta

def parse_date(ts):
    '''
    Parse syslog date with optional sub-second precision.
    '''
    if '.' in ts:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.%f")
    else:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")

def parse_timestamp(ts):
    '''
    Parse timestamps in these formats to a datetime structure:
    '2003-10-11T22:14:15.003000Z'
    '2003-10-11T22:14:15.003Z'
    '2003-10-11T22:14:15Z'
    '2003-10-11T22:14:15.003000-07:00'
    '''
    if ts == '-':
        timestamp = None
    elif ts[-1] == 'Z':
        timestamp = parse_date(ts[:-1])
    else:
        timestamp = parse_date(ts[:-6])
        hours = int(ts[-5:-3])
        mins = int(ts[-2:])
        sign = ts[-6] == '-' and -1 or 1
        timestamp += timedelta(seconds=sign*(hours*3600+mins*60))

    return timestamp
