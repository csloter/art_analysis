# -*- coding:utf-8 -*-
'''
Created on 2014-10-31

@author: csloter@163.com
'''
import datetime

def past_day( i ):
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
if __name__ == '__main__':
    print now()