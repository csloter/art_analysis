# -*- coding:utf-8 -*-
'''
Created on 2014-11-29

@author: csloter@163.com
'''

import sys,os,time,redis,traceback,json,logging
from aggreation.art2_api_es import Art2ApiLogEs
from util import yaml_conf 

#配置信息
conf_map = yaml_conf.conf
DB_INDEX = 0
REDIS_ART_LOG_PATH = conf_map['redis']['sub']['log']
logging.basicConfig(filename=REDIS_ART_LOG_PATH,level=logging.INFO,format='%(asctime)s - %(message)s')
LOG = logging.getLogger()
ART_CHANNEL = conf_map['redis']['sub']['art_channel']
ART_CHANNEL_UNCOSUME = conf_map['redis']['sub']['art_channel_unconsume']
REDIS_HOST = conf_map['redis']['host']

class ArtLogSub(object):
    ''' redis '''
    def __init__ (self,host,port,db_index):
        self.host = host
        self.port = port
        self.db_index = db_index
        try:
            pool = redis.ConnectionPool(host = self.host, port = self.port, db = self.db_index )
            LOG.info( 'redis conn success. ip:[%s],port:[%d],db:[%d]' % ( self.host, self.port, self.db_index ) )
            self.conn  = redis.Redis(connection_pool=pool)
            self.sub = self.conn.pubsub( ignore_subscribe_messages=True)
            LOG.info( 'redis subscribe ok. ' )
        except:
            LOG.error( traceback.format_exc() )
        self.art_es = Art2ApiLogEs()

    def art_sub( self ):
        '''sub'''
        #self.sub.subscribe( **{channel: self.art_handler} )
        # for msg in self.sub.listen():
        #     if msg['data'] == 'KILL':
        #         print 'kill'
        #     print msg
        self.sub.subscribe( ART_CHANNEL )
        while True:
            message = self.sub.get_message()
            if message:
                message_data = message['data']
                if  message_data== 'KILL':
                    break
                self.art_es.split_log( message_data )
            time.sleep( 0.001 )
        self.sub.close()
        LOG.info( '[' + ART_CHANNEL + '] closeed ')

    def art_sub_unconsume( self ):
        '''sub'''
        #self.sub.subscribe( **{channel: self.art_handler} )
        # for msg in self.sub.listen():
        #     if msg['data'] == 'KILL':
        #         print 'kill'
        #     print msg
        self.sub.subscribe( ART_CHANNEL_UNCOSUME )
        LOG.info( '[' + ART_CHANNEL_UNCOSUME + '] closeed ' )
        while True:
            message = self.sub.get_message()
            if message:
                message_data = message['data']
                if  message_data== 'KILL':
                    break
                self.art_es.split_log( message_data )
            time.sleep( 0.001 )
        self.sub.close()
        LOG.info( '[' + ART_CHANNEL_UNCOSUME + '] closeed ')

    def art_handler( self, message ):
        ''''''
        print message['data']
    

if __name__ == '__main__':
    r = ArtLogSub(REDIS_HOST, 6379, 0)
    r.art_sub()
    #print dir( r.pipe)
