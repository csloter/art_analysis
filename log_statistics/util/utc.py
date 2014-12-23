# -*- coding:utf-8 -*-
'''
Created on 2014-10-29

@author: csloter@163.com
'''
from datetime import tzinfo, timedelta, datetime

# A UTC class.

class GMT8(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return timedelta( hours=8 )

    def tzname(self, dt):
        return "GMT8"

    def dst(self, dt):
        return timedelta( hours=8 )

class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return timedelta( hours=-8 )

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return timedelta( hours=-8 )

gmt8 = GMT8()
utc = UTC()