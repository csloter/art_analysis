# -*- coding:utf-8 -*-
'''
Created on 2014-11-29

@author: csloter@163.com
'''

import sys,os,time,redis,traceback,json,logging

DB_INDEX = 0
LOG_PATH = r'D:\tt.log'
logging.basicConfig(filename=LOG_PATH,level=logging.INFO,format='%(asctime)s - %(message)s')
LOG = logging.getLogger()
queue = 'art_queue'

class ArtLogSub(object):
    ''' redis '''
    def __init__ (self,host,port,db_index):
        self.host = host
        self.port = port
        self.db_index = db_index
        try:
            pool = redis.ConnectionPool(host = self.host, port = self.port, db = self.db_index)
            self.conn  = redis.Redis(connection_pool=pool)
            self.sub = self.conn.pubsub( )
        except:
            print traceback.format_exc()

    def art_sub( self ):
        '''sub'''
        self.sub.subscribe( queue )
        print dir( self.sub )
        for msg in self.sub.listen():
           print msg

    

if __name__ == '__main__':
    r = ArtLogSub('127.0.0.1', 6379, 0)
    r.art_sub()
    #print dir( r.pipe)
