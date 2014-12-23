# -*- coding:utf-8 -*-
'''
Created on 2014-10-28

@author: csloter@163.com
'''
import xlwt
import os

wbk = xlwt.Workbook( encoding='utf8' )
summary_sheet = wbk.add_sheet( '概述' )
current_row = 0
summary_sheet.write_merge( current_row, current_row , 0, 0, '登录' )
summary_sheet.write_merge( current_row, current_row , 1, 2, '登录1')
xls_name = 'test.xls'
xls_path = r'd:/'
wbk.save( os.path.join( xls_path, xls_name ) )