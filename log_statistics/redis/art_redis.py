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

class ArtRedis(object):
    ''' redis '''
    def __init__ (self,host,port,db_index):
        self.host = host
        self.port = port
        self.db_index = db_index
        try:
            pool = redis.ConnectionPool(host = self.host, port = self.port, db = self.db_index)
            self.conn  = redis.Redis(connection_pool=pool)
            self.pipe = self.conn.pipeline()
        except:
            traceback.format_exc()

    def redis_set(self,keys=None ,values=None):
        ''' just set key:value'''
        try:
            self.pipe.set(keys,values )
            self.pipe.execute()
        except:
            LOG.error( traceback.format_exc() )
            return traceback.format_exc()

    def redis_get(self,keys=None ,values=None):
        ''' get Key's values '''
        try:
            self.pipe.get(keys )
            return self.pipe.execute()[0]
        except:
            LOG.error( traceback.format_exc() )
            print traceback.format_exc()

    def redis_sadd(self, keys=None, values=None ):
        ''' redis set 添加'''
        try:
            for v in values:
                self.pipe.sadd( keys, v)
            print self.pipe.execute()
        except:
            LOG.error( traceback.format_exc() )
            print traceback.format_exc()

    def redis_smembers(self, keys=None ):
        ''' redis set 获取所有参数'''
        try:
            self.pipe.smembers(keys)
            return self.pipe.execute()[0]
        except:
            LOG.error( traceback.format_exc() )
            print traceback.format_exc()
    
    def redis_sismember(self, keys=None, member=None):
        '''keys set集合是否包含 member'''
        try:
            self.pipe.sismember( keys, member )
            return self.pipe.execute()[0]
        except:
            LOG.error( traceback.format_exc() )
            print traceback.format_exc()

if __name__ == '__main__':
    r = ArtRedis('127.0.0.1', 6379, 0)
    #r.redis_set('t', 'te')
    print r.redis_smembers('t2')
    print r.redis_sismember( 't1', '2') 
    print r.redis_get('22')
    #print dir( r.pipe)
