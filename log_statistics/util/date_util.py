# -*- coding:utf-8 -*-
'''
Created on 2014-10-31

@author: csloter@163.com
'''
import datetime
from util import utc

def past_day( i ):
    '''住前 i 天'''
    return datetime.datetime.now() + datetime.timedelta(days=-i)

def past_day_Y_m_D_str( i ):
    return  past_day( i ).strftime( '%Y-%m-%d' )

def past_day_YmD_str( i ):
    return  past_day( i ).strftime( '%Y%m%d' )

def y_m_d_H_M_date( date_str):
    ''''''
    return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M')

def past_minutes( i ):
    return datetime.datetime.now() + datetime.timedelta(minutes=-i)

def now( ):
    return datetime.datetime.now().strftime( '%Y-%m-%d %H:%M:%S' )  

def y_m_d_H_M_S_date( date_str):
    ''''''
    return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

def now_utc( ):
    ''''''
    return datetime.datetime.utcnow()
    # print d
    # return  datetime.datetime( d.year, d.month, d.day, d.hour, d.minute, d.second, tzinfo = utc.utc )

def day_YmD_str():
    return datetime.datetime.now().strftime( '%Y%m%d' )

def past_utc_minutes( i ):
    return datetime.datetime.utcnow() + datetime.timedelta(minutes=-i)

def y_m_d_H_M_S_utc_date( date_str):
    '''hour -8'''
    return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(hours=-8)

def timestamp_to_utc_datetime( timestamps ):
    '''时间戳转为utc时间'''
    try:
        return datetime.datetime.fromtimestamp( int(timestamps)/1000.0 ) + datetime.timedelta(hours=-8)
    except:
        return datetime.datetime.utcnow()

if __name__ == '__main__':
    print timestamp_to_utc_datetime(1419839097907)
    import time
    print time.time()
