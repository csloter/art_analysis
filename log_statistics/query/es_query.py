# -*- coding:utf-8 -*-
'''
Created on 2014-11-29

@author: csloter@163.com
'''
from elasticsearch import Elasticsearch
from util import date_util
from util import yaml_conf 

#配置信息
conf_map = yaml_conf.conf
ES_INDEX = conf_map['es']['index']
ES_TYPE = conf_map['es']['type']
ES_CLUSTER = conf_map['es']['cluster']
HOSTS = conf_map['es']['hosts']

class Es(object):
    '''just es '''

    def __init__( self ):
        '''es'''
        hosts = HOSTS
        self.es_client = Elasticsearch( hosts, cluster=ES_CLUSTER )
        #print self.es_client.info(

    def index( self , doc):
        '''索引信息
            id : userid
            doc : {}
        '''
        art_index = ES_INDEX + '_' + date_util.day_YmD_str() 
        res = self.es_client.index(index=art_index, doc_type=self.es_type, body=doc)

    def register_users( self ):
        '''注册用户'''
        query = {
            'query': {
                "filtered": {
                  "query": { "match": { "api": "v1userregister" }},
                    "filter": {
                      "range": { 
                        "v_time": {"gte": date_util.past_utc_minutes( 5 )  }
                      }
                    }
                 }
              }
        }
        response = self.es_client.search( body=query )
        return response['hits']['total']

    def 
if __name__ == '__main__':
    e = Es()
    #e.delete( '547330e9d0d34a6048cfffce')
    # d_id = '11111'
    # doc = { 'my_list':[1,2] }
    # script='if (ctx._source.containsKey("my_list")) {ctx._source.my_list += 4;} else {ctx._source.paymentInfos = [5]}'
    # print script
    # e.upsert( d_id, doc, doc, script )
    #import datetime
    #a = {'name': 'name1', 'val': None, 'on_line':True, 'register_date': datetime.datetime.now(), 'online_time':datetime.datetime.now(), 'upload_img_time': datetime.datetime.now() }
    # query = {
    #     'query':{
    #         'filtered' :{
    #             'filter':{
    #                 #'term' : {'userid':'546d40dfcb08b20518bff6b7'}
    #                 'range' :{
    #                     'v_time':{'gte': date_util.past_utc_minutes(10)}
    #                 }
    #             }

    #         }
    #     }
    # }
    print date_util.past_utc_minutes(100) 
    print e.register_users( )
