# -*- coding:utf-8 -*-
'''
Created on 2014-10-28

@author: csloter@163.com
'''

import logging
logger = logging.getLogger() 
filehandler = TimedRotatingFileHandler(logFile) 
fmt = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(message)s')
filehandler.setFormatter(fmt)
logger.setLevel(logging.INFO)
logger.addHandler(filehandler)

logger.info( '111' )
