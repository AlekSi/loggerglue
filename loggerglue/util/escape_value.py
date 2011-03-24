import re

escape_re = re.compile(r'([\"\\\]])')

def escape_param_value(s):
    '''
    Escape PARAM-VALUE. Inside PARAM-VALUE, the characters '"' (ABNF %d34), '\' (ABNF %d92),
    and ']' (ABNF %d93) MUST be escaped.
    '''
    return escape_re.sub(r'\\\1', s)

def str_or_nil(s):
    '''
    Return the string value of s, or NILVALUE if s is None.
    '''
    if s is None:
        return '-'
    else:
        return str(s)

        