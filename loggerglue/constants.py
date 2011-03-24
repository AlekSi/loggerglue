"""The syslog constants are replicated here because not all systems have the (binary) syslog module. 
RFC5424 priority values are a combination of a priority and facility code, for example:

    prival = LOG_ALERT | LOG_DAEMON

Priorities
----------

============== =====================
Constant        Description
============== =====================
LOG_EMERG       System is unusable
LOG_ALERT       Action must be taken immediately
LOG_CRIT        Critical conditions
LOG_ERR         Error conditions
LOG_WARNING     Warning conditions
LOG_NOTICE      Normal but significant condition
LOG_INFO        Informational
LOG_DEBUG       Debug-level messages
============== =====================

Facility codes
--------------

=============  ===========================================
Constant        Description
=============  ===========================================
LOG_KERN        Kernel messages
LOG_USER        Random user-level messages
LOG_MAIL        Mail system
LOG_DAEMON      System daemons
LOG_AUTH        Security/authorization messages
LOG_SYSLOG      Messages generated internally by syslogd
LOG_LPR         Line printer subsystem
LOG_NEWS        Network news subsystem
LOG_UUCP        UUCP subsystem
LOG_CRON        Clock daemon
LOG_AUTHPRIV    Security/authorization messages (private)
LOG_LOCAL0      Reserved for local use
LOG_LOCAL1      Reserved for local use
LOG_LOCAL2      Reserved for local use
LOG_LOCAL3      Reserved for local use
LOG_LOCAL4      Reserved for local use
LOG_LOCAL5      Reserved for local use
LOG_LOCAL6      Reserved for local use
LOG_LOCAL7      Reserved for local use
=============  ===========================================
"""

LOG_EMERG     = 0
LOG_ALERT     = 1
LOG_CRIT      = 2
LOG_ERR       = 3
LOG_WARNING   = 4
LOG_NOTICE    = 5
LOG_INFO      = 6
LOG_DEBUG     = 7

LOG_KERN      = 0<<3
LOG_USER      = 1<<3
LOG_MAIL      = 2<<3
LOG_DAEMON    = 3<<3
LOG_AUTH      = 4<<3
LOG_SYSLOG    = 5<<3
LOG_LPR       = 6<<3
LOG_NEWS      = 7<<3
LOG_UUCP      = 8<<3
LOG_CRON      = 9<<3
LOG_AUTHPRIV  = 10<<3
LOG_LOCAL0    = 16<<3
LOG_LOCAL1    = 17<<3
LOG_LOCAL2    = 18<<3
LOG_LOCAL3    = 19<<3
LOG_LOCAL4    = 20<<3
LOG_LOCAL5    = 21<<3
LOG_LOCAL6    = 22<<3
LOG_LOCAL7    = 23<<3

