# -*- coding:utf-8 -*-
'''
Created on 2014-10-29

@author: csloter@163.com
'''
import db

class Dao( object ):
	'''
	'''
	def __init__( self ):
		self.conn = db.conn()

	def get_exist_users( self ):
		sql = 'select userid from exists_users'
		cursor = self.conn.cursor()
		cursor.execute( sql )
		row = cursor.fetchall()
		cursor.close()
		
	def insert_exist_users( self, values ):
		sql = 'insert IGNORE exists_users ( userid ) values (%s)'
		cursor = self.conn.cursor()
		cursor.executemany( sql, values )
		self.conn.commit()
		cursor.close()

	def insert_userid_unique_device_no( self, values ):
		'''用户id与imei OR udid 对应关系'''
		sql = 'INSERT INTO userid_unique_device_no ( device_no, userid, channel_no ) VALUES ( %s,%s,%s )'
		self.insert_batch( sql, values )

	def query_unique_device_nos( self ):
		'''查询已有的imei OR udid'''
		sql = 'SELECT device_no from  userid_unique_device_no '
		return self.query_all( sql )

	def query_unique_device_no( self, device_no):
		'''查询 imei'''
		sql = 'SELECT device_no from userid_unique_device_no where device_no = %s'
		return self.query_one( sql, device_no )

	def insert_channel_use( self, values ):
		'''渠道维度的使用情况
		channel_no, channel_name,boot_times,new_users,new_register_users, `date`
		'''
		sql = '''INSERT INTO channel_use (channel_no, channel_name,boot_times,new_users,new_register_users, `date`)
				 VALUES( %s,%s,%s,%s,%s,%s )'''
		self.insert_batch( sql, values )

	def insert_op_log( self, value ):
		'''操作记录表'''
		sql = '''INSERT INTO op_log ( op_name, op_date ) values ( %s, %s )'''
		self.insert_one( sql, value )
    
	def query_op_log( self, value ):
		''''''
		sql = ' SELECT id FROM op_log WHERE op_name =%s AND op_date = %s'
		return self.query_one( sql, value)
		
	def query_one( self, sql, value ):
		''''''
		cursor = self.conn.cursor()
		cursor.execute( sql, value )
		row = cursor.fetchone()
		return row

	def query_all( self, sql ):
		''''''
		cursor = self.conn.cursor()
		cursor.execute( sql )
		return cursor.fetchall()

	def insert_one( self, sql ,value ):
		''''''
		cursor = self.conn.cursor()
		cursor.execute( sql, value )
		self.conn.commit()
		cursor.close() 

	def insert_batch( self, sql, values ):
		'''批量插入'''
		cursor = self.conn.cursor()
		cursor.executemany( sql, values )
		self.conn.commit()
		cursor.close() 

	def __del__( self ):
		if self.conn:
			self.conn.close()


if __name__=="__main__":
	dao = Dao()
	#values =(('channel_no','channel_name', 121,10,20,'2014-10-30'),('channel_no','channel_name', 123,10,20,'2014-10-30'))
	#dao.insert_channel_use( values )
	#dao.insert_op_log( values )
	#dao.insert_userid_unique_device_no([('111','222')])
	print dao.query_unique_device_no( '864264023097949' )