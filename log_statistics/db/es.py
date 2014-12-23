# -*- coding:utf-8 -*-
'''
Created on 2014-11-29

@author: csloter@163.com
'''
from elasticsearch import Elasticsearch
from util import date_util
ES_INDEX = 'art_index'
ES_TYPE = 'art_type'
ES_CLUSTER = 'art_cluster'

class Es(object):
    '''just es '''

    def __init__(self, es_index=None, es_type=None):
        '''es'''
        hosts = ['localhost:9200']
        if es_index:
            self.es_index = es_index
        else:
            self.es_index = ES_INDEX
        if es_type:
            self.es_type = es_type
        else:
            self.es_type = ES_TYPE;
        self.es_client = Elasticsearch( hosts, cluster=ES_CLUSTER )
        #print self.es_client.info()

    def index( self , d_id, doc):
        '''索引信息
            id : userid
            doc : {}
        '''
        res = self.es_client.index(index=self.es_index, doc_type=self.es_type, id=d_id, body=doc)
        print res['created']

    def search( self, query):
        '''q'''
        response = self.es_client.search( index=self.es_index, doc_type=self.es_type, body=query)
        print response['hits']['total']

    def delete( self, doc_id ):
        '''delete'''
        self.es_client.delete(index=self.es_index, doc_type=self.es_type, id=doc_id )

    def upsert( self, doc_id, doc_update, doc_index, script=None ):
        '''添加更新'''
        try:
            self.es_client.update( index=self.es_index, doc_type=self.es_type, id=doc_id, body=doc_update,  script=script, lang='mvel' )
        except Exception, e:
            print e
            self.index( doc_id, doc_index )

if __name__ == '__main__':
    e = Es( ES_INDEX, ES_TYPE)
    e.delete( '54794d358f7122db4d1f248a')
    d_id = '11111'
    doc = { 'my_list':[1,2] }
    script='if (ctx._source.containsKey("my_list")) {ctx._source.my_list += 4;} else {ctx._source.paymentInfos = [5]}'
    print script
    e.upsert( d_id, doc, doc, script )
    #import datetime
    #a = {'name': 'name1', 'val': None, 'on_line':True, 'register_date': datetime.datetime.now(), 'online_time':datetime.datetime.now(), 'upload_img_time': datetime.datetime.now() }
    # query = {
    #     'query':{
    #         'filtered' :{
    #             'filter':{
    #                 #'term' : {'userid':'546d40dfcb08b20518bff6b7'}
    #                 'range' :{
    #                     'online_time':{'gte': date_util.past_minutes(10)}
    #                 }
    #             }

    #         }
    #     }
    # }
    # print query
    # e.search( query )
