# -*- coding:utf-8 -*-
'''
Created on 2014-10-28

@author: csloter@163.com
'''
import re
import os.path
import json
import xlwt
import constants
import gzip
from util import yaml_conf 
from db.mongo_dao import MongoDbDao
from db.dao import Dao
from util import mail_sender
from util import date_util

#配置信息
conf_map = yaml_conf.conf
#无效字段
UNKNOW_VALUE = 'undefined'
#渠道对应关系
ALL_CHANNEL = constants.CHANNELS
#其他渠道
CHANNEL_OTHER = 'other'

#注册成功会打/v1/studentselfprofile OR /v1/teracherselfprofile
REGISTER_RESPONSE_STUDENT = '/v1/studentselfprofile'
REGISTER_RESPONSE_TERACHER = '/v1/teracherselfprofile'
REGISTER_RESPONSE = '/v1/userregister'


class ApiResponse( object ):
	''''''
	def __init__(self, date):
		'''
		date : %Y-%m-%d
		'''
		self.date = date
		# try:
		# 	self.mongo_dao = MongoDbDao() 
		# 	self.exists_users = mongo_dao.exists_users()
		# except Exception , ex:    
		# 	print Exception, ex 
		self.mongo_dao = MongoDbDao()
		self.exists_unique_device_nos = self.mongo_dao.query_exists_device_nos()
		self.xls_name = os.path.join( conf_map['xls']['path'], '-'.join( ( self.date, conf_map['xls']['name']) ) )


	def do_header( self, line ):
		'''处理header信息'''
		line_arr = line.split( '<|>' )
		print len(line_arr)
		if len( line_arr) != 12:
			return
		lines = {}
		v_time = line_arr[0][:16]
		lines['v_time'] = v_time
		sversion = line_arr[0][16:].split( 'sversion:' )[1]
		lines['sversion'] = sversion
		for i in range( 1, len(line_arr)):
			self.putStr( line_arr[i], lines )
		return lines
		
	def putStr( self, sub_line,lines={} ):
		''''''
		k = sub_line.split( ':' )[0]
		v = sub_line.split( ':' )[1]
		lines[k] = v

	def msg_api_resposne_log( self ):
		#统计日期，一般是昨天
		log = os.path.join( conf_map['log']['path']['api'], '.'.join( ('meishubao_response.log',self.date,'gz' ) ) )
		#只统计header信息
		#启动次数
		self.channel_boot ={}
		#新增用户,需要排除所有已注册用户
		self.channel_new_users = {}
		#所有渠道
		self.channels = set()
		#渠道注册用户
		self.channel_registers = {}
		#只统计下一行的信息
		#header 行
		is_header_line = False
		#request 行
		is_request_line = False
		#response 行
		is_response_line = False
		self.unique_device_nos = {}
		count = 0
		with gzip.open( log ) as log_file:
			line_map = {}
			details = []
			for line in log_file:
				api = ''
				
				line = line.strip()
				if not line:
					continue 
				if line.startswith('@response'):
					api = line[line.index('/'):]
					is_header_line = True
					continue
				if is_header_line:
					line_map = self.do_header( line )
					#print api
					if not line_map:
						continue
					channel = line_map.get( 'channel' )
					if channel == UNKNOW_VALUE:
						channel = CHANNEL_OTHER
					print channel
					self.channels.add( channel )
					userid = line_map.get( 'userid' )
					#启动次数 调用次数
					if api == '/v1/initinfo':
						self.channel_boot.setdefault( channel, [] ).append('')
					
					is_request_line = True
					is_header_line = False
					continue

				if is_request_line:
					is_response_line = True
					is_request_line = False
					continue

				if is_response_line:
					if api == REGISTER_RESPONSE:
						json_map = json.loads( line.split( 'info:' )[1] )
						register_user_channel = json_map.get( 'channel' )
						register_user_id = json_map.get( 'userid' )
						if not register_user_channel or register_user_channel == UNKNOW_VALUE:
							register_user_channel = CHANNEL_OTHER
						line_map['channel'] = register_user_channel
						self.channel_registers.setdefault( register_user_channel, set() ).add( register_user_id )
					is_response_line = False
				imei = line_map.get('imei')
				udid = line_map.get('udid')
				if self.is_valid_imei( imei ) and not self.is_device_exists( imei ):
					#新增用户
					self.channel_new_users.setdefault( channel, set() ).add( imei )
					unique_devices =  self.get_unique_device_nos( line_map )
					unique_devices['_id'] = imei 
					self.add_unique_device_nos( imei, unique_devices )
				elif self.is_valid_udid( udid ) and  not self.is_device_exists( udid ):
					#新增用户
					self.channel_new_users.setdefault( channel, set() ).add( udid )
					unique_devices =  self.get_unique_device_nos( line_map )
					unique_devices['_id'] = udid 
					self.add_unique_device_nos( udid, unique_devices )
				if line_map:
					details.append( line_map )
					if count % 1000 == 0:
						self.save_log_detail( details  )
						details = []
						count = 0
				line_map = {}
			if count != 0 :
				self.save_log_detail( details )
			if not self.mongo_dao.query_op_log( 'DETAIL', self.date ):
				self.mongo_dao.add_op_log( 'DETAIL', self.date )

	def save_log_detail( self, details ):
		'''保存明细数据到mongodb'''
		if self.mongo_dao.query_op_log( 'DETAIL', self.date ):
			return
		self.mongo_dao.bulk_add_detail( 'log_detail_' + self.date.replace('-',''), details )
	def get_unique_device_nos( self, line_map):
		''''''
		unique_device_map = {}
		if 'sversion' in line_map:
			unique_device_map['sversion'] = line_map.get('sversion', '-')
		if 'cversion' in line_map:
			unique_device_map['cversion'] = line_map.get('cversion', '-')
		if 'cversion' in line_map:
			unique_device_map['cversion'] = line_map.get('cversion', '-')
		if 'imei' in line_map:
			unique_device_map['imei'] = line_map.get('imei', '-')
		if 'platform' in line_map:
			unique_device_map['platform'] = line_map.get('platform', '-')
		if 'deviceid' in line_map:
			unique_device_map['deviceid'] = line_map.get('deviceid', '-')
		if 'userid' in line_map:
			unique_device_map['userid'] = line_map.get('userid', '-')
		if 'channel' in line_map:
			unique_device_map['channel'] = line_map.get('channel', '-')
		if 'udid' in line_map:
			unique_device_map['udid'] = line_map.get('udid', '-')
		return unique_device_map

	def add_unique_device_nos( self, unique_device_no, unique_device_map ):
		''''''
		device_nos = self.unique_device_nos.setdefault( unique_device_no, unique_device_map )
		userid = device_nos.get( 'userid', UNKNOW_VALUE )
		if userid and userid != UNKNOW_VALUE:
			device_nos['userid'] = userid
		channel_no = device_nos.get( 'channel', UNKNOW_VALUE )
		if channel_no and channel_no != UNKNOW_VALUE:
			device_nos['channel'] = channel_no


	def to_excel( self ):
		''''''
		#执行日志计算
		self.msg_api_resposne_log()

		wbk = xlwt.Workbook( encoding='utf8' )
		#head
		head_style = xlwt.easyxf('align: wrap off, vert centre, horiz center; pattern: pattern solid, fore-colour gray40')
		head_style.font.height = 0xdc
		sheet = wbk.add_sheet( '渠道（按天）' )
		current_row = 0
		sheet.write_merge( current_row, current_row , 0, 0, '渠道号', head_style )
		sheet.write_merge( current_row, current_row , 1, 1, '渠道名称', head_style )
		sheet.write_merge( current_row, current_row , 2, 3, '新增用户数', head_style  )
		sheet.write_merge( current_row, current_row , 4, 5, '注册用户数', head_style )
		sheet.write_merge( current_row, current_row , 6, 7, '当天启动次数', head_style )
		channels = list( self.channels )
		channels.sort()
		values = []
		for channel_no in channels:
			print channel_no
			use_map = {}
			current_row += 1
			channel_name = ALL_CHANNEL.get( channel_no, u'其他')
			new_users = len( self.channel_new_users.get( channel_no, [] ) )
			new_register_users = len( self.channel_registers.get( channel_no, [] ) )
			channel_boots = len( self.channel_boot.get( channel_no, [] ) ) 
			sheet.write_merge( current_row, current_row , 0, 0, channel_no  )
			sheet.write_merge( current_row, current_row , 1, 1, channel_name )
			sheet.write_merge( current_row, current_row , 2, 3, new_users )
			sheet.write_merge( current_row, current_row , 4, 5, new_register_users )
			sheet.write_merge( current_row, current_row , 6, 7, channel_boots )
			use_map['channel_no'] = channel_no
			use_map['channel_name'] = channel_name
			use_map['channel_boots'] = channel_boots
			use_map['new_users'] = new_users
			use_map['new_register_users'] = new_register_users
			use_map['date'] = self.date
			values.append( use_map )
		#结果保存到db
		self.save( values ) 
		#写到文件
		wbk.save( self.xls_name )

	def mail_send( self ):
		'''发送邮件'''
		self.to_excel()
		to = conf_map['mail']['to']
		to_me = conf_map['mail']['to_me']
		subject = self.date + u'日报' 
		text = u'美术宝日报 (response 新日志)'
		mail_sender.send_email_attach( to, subject, text, [ self.xls_name ])
		mail_sender.send_email_attach( to_me, subject, text, [ self.xls_name ])

	def save( self, values ):
		'''保存数据到db'''
		try:
			if not self.mongo_dao.query_op_log( 'API', self.date ):
				self.mongo_dao.add_channel_use( values )
				self.mongo_dao.add_op_log( 'API', self.date )
			
			for k in self.unique_device_nos:
				self.mongo_dao.upset_unique_device_no( self.unique_device_nos.get( k ) )
		except Exception , ex:
			print Exception , ex


	def is_valid_imei( self, imei ):
		'''是否是有效imei'''
		return ( imei and imei != UNKNOW_VALUE 
				and not imei.startswith('a') 
				and not imei.startswith('h')
				and not imei.startswith('p') 
				and imei != 'msb-web'
				and imei != 'msb-apk'
				and imei != 'msg-iphone' )

	def is_valid_udid( self, udid ):
		'''是否是有效的udid'''
		return ( udid and udid != UNKNOW_VALUE 
				and not udid.startswith('a') 
				and not udid.startswith('h')
				and not udid.startswith('p') 
				and udid != 'msb-web'
				and udid != 'msb-apk'
				and udid != 'msg-iphone' )

	def is_device_exists( self, device_no ):
		'''是否已经存在'''
		return self.exists_unique_device_nos and device_no in self.exists_unique_device_nos

if __name__ == '__main__':
	#log = LogAnalysis( date_util.past_day_Y_m_D_str(1) )
	log = ApiResponse( '2014-11-21')
	log.to_excel()
# 2 save userids
# 3 to excel
# 4 send mail