# coding:utf-8
'''
Created on 2014-10-28

@author: csloter
'''

from util import yaml_conf 
import MySQLdb
from DBUtils.PooledDB import PooledDB

conf_map = yaml_conf.conf

class DbConfig(object):
    '''数据库配置'''
    #使用的连接接口
    dbapi=MySQLdb
    #主机ip
    host= conf_map['db']['host']
    #端口
    port= conf_map['db']['port']
    #数据库名
    database_name=conf_map['db']['name']
    #用户名
    username=conf_map['db']['username']
    #密码
    password=conf_map['db']['password']
    #最小连接数
    mincached=5
    #最大连接数
    maxcached=10
    
    #使用unicode
    use_unicode=True
    #字符编码为utf8
    charset='utf8'

    
#统计库的连接池    
db_pool_stat = PooledDB(creator=DbConfig.dbapi, mincached=DbConfig.mincached, maxcached=DbConfig.maxcached, 
                  host=DbConfig.host, port=DbConfig.port, user=DbConfig.username,
                  passwd=DbConfig.password, db=DbConfig.database_name, 
                  use_unicode=DbConfig.use_unicode,charset=DbConfig.charset )

def conn():
    return  db_pool_stat.connection()
def close():
    db_pool_stat.close()
  
if __name__=="__main__":
    conn = conn()
    print conn
