# -*- coding:utf-8 -*-
'''
Created on 2014-10-29

@author: csloter@163.com
'''
from pymongo import MongoClient
from util import yaml_conf 
from datetime import datetime
from util import utc
#配置信息
conf_map = yaml_conf.conf

class MongoDbDao( object ):
	''''''
	def __init__(self):
		''''''
		#self.client = MongoClient( conf_map['mongo']['uri'] )
		self.client_log_stats = MongoClient( conf_map['mongo_log_stats']['uri'] ) 
		dbs = conf_map['mongo_log_stats']['dbs'].split(',')
		self.db_pool = {}
		for db_name in dbs:
			db = self.get_db( self.client_log_stats, db_name )
			if self.auth( db, db_name ):
				self.db_pool[db_name] = db 

	def get_db(self, client, db_name ):
		#return self.client[db_name]
		return client[db_name]

	def auth( self, db, db_name ):
		'''是否需要验证'''
		return not conf_map[db_name]['is_auth'] or  db.authenticate( conf_map[db_name]['username'], conf_map[db_name]['password'] )

	def upset_unique_device_no( self, values={} ):
		'''imei | udid --> userid & channel_no & sverion & cversion & platform & ip_x & last_time'''
		if not values:
			return
		table = self.db_pool.get( 'stats' )['unique_device_nos']
		table.save( values )

	def bulk_add_detail( self, table_name, details=[{}] ):
		'''log 明细，just add. table name is table'''
		if not details:
			return
		table = self.db_pool.get( 'stats' )[table_name]
		table.insert( details )

	def query_exists_device_nos( self ):
		'''查询已经保存的设备imei OR udid '''
		table = self.db_pool.get( 'stats' )['unique_device_nos']
		device_nos = set()
		for unique_device in table.find():
		 	device_nos.add( unique_device.get( '_id' ) )
		return device_nos

	def add_op_log( self, op_name, op_date ):
		'''操作记录表'''
		table =  self.db_pool.get( 'stats' )['op_log']
		table.save({'op_name' : op_name, 'op_date' : op_date } )

	def query_op_log( self, op_name, op_date ):
		'''查询是否已经操作，防止重复插入'''
		table =  self.db_pool.get( 'stats' )['op_log']
		return table.find_one( {'op_name' : op_name, 'op_date' : op_date } )

	def add_channel_use( self, values=[{}] ):
		'''渠道维度的使用情况 map
		channel_no, channel_name,boot_times,new_users,new_register_users, `date`
		{channel_no : channel }...
		'''
		if not values:
			return
		table =  self.db_pool.get( 'stats' )['channel_use']
		table.insert( values )

	def exists_users( self  ):
		'''查询已经注册的所有用户'''
		user_table = self.db_pool.get( 'meishubao')['users']
		# to ISODate
		#q = { 'create_at' : { '$gt' : self.iso_date( start ), '$lt' : self.iso_date( end ) } }
		users = []
		for user in  user_table.find( ):
			#print type(str( a['_id'] ))
			users.append( user['_id'] )
		return users

	def register_users( self, date_str ):
		'''查询当天注册用户
			date_str = %Y-%m-%d
		'''
		user_table = self.db_pool.get( 'meishubao')['users']
		# to ISODate
		q = { 'create_at' : { '$gt' : self.iso_datetime( date_str +' 00:00:00' ), '$lt' : self.iso_datetime( date_str + ' 23:59:59') } }
		users = []
		for user in  user_table.find( q ):
			#print type(str( a['_id'] ))
			users.append( str( user['_id'] ) )

		return users

	def iso_date( self, date_str ):
		'''mongodb保存的是isodate '''
		date_arr = self.date_str_2_int( date_str )
		return 	datetime( date_arr[0], date_arr[1], date_arr[2],  tzinfo= utc.gmt8 )

	def iso_datetime( self, date_time_str ):
		'''mongodb保存的是isodate '''
		d = datetime.strptime( date_time_str, '%Y-%m-%d %H:%M:%S')
		return 	datetime( d.year, d.month, d.day, d.hour, d.minute, d.second, tzinfo = utc.utc )

	def date_str_2_int( self, date_str ):
		''''''
		return map( lambda a: int(a), date_str.split( '-' ) )

#mongo_dao = MongoDbDao()

if __name__ == '__main__':
	dao = MongoDbDao()
	#db = dao.getDb( 'search_mysql')
	print dao.query_exists_device_nos( )
	#print datetime('2014','10','30','17', tzinfo= utc.gmt8 ) 
	#d = datetime.strptime('2013-12-12 12:12:12', '%Y-%m-%d %H:%M:%S' )
	#print dao.iso_datetime( '2013-12-12 12:12:12' )
	#print datetime.now()


