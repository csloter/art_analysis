# -*- coding:utf-8 -*-
'''
Created on 2014-11-01

@author: csloter@163.com
'''
from aggreation.art2_api  import Art2ApiLog
from util import date_util
import getopt
import sys

opts, args = getopt.getopt(sys.argv[1:], '', ['start='])
start = ''
for op, value in opts:
    if op == '--start':
        start = value
if not start:
    print 'start is MUST! --start today | 2014-11-01'
    sys.exit()
if start.lower() == 'today':
   log = Art2ApiLog( date_util.past_day_Y_m_D_str(1) )
   log.mail_send()
else :
   log = Art2ApiLog( start )
   log.mail_send()