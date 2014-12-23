# -*- coding:utf-8 -*-
'''
Created on 2014-10-28

@author: csloter@163.com
'''
import re
import os.path
import json
import gzip
import xlwt
import constants
from util import yaml_conf 
from db.mongo_dao import MongoDbDao
from db.dao import Dao
from util import mail_sender
from util import date_util

#配置信息
conf_map = yaml_conf.conf
#无效字段
UNKNOW_VALUE = '-'
#渠道对应关系
ALL_CHANNEL = constants.CHANNELS
#其他渠道
CHANNEL_OTHER = 'other'

#注册成功会打/v1/studentselfprofile OR /v1/teracherselfprofile
REGISTER_RESPONSE_STUDENT = '/v1/studentselfprofile'
REGISTER_RESPONSE_TERACHER = '/v1/teracherselfprofile'
REGISTER_RESPONSE = '/v1/userregister'
#log 文件名称
LOG_FILE_NAME = 'meishubao_api.log'

class Art2ApiLog( object ):
	''''''
	def __init__(self, date):
		'''
		date : %Y-%m-%d
		'''
		self.date = date
		self.mongo_dao = MongoDbDao()
		self.exists_unique_device_nos = self.mongo_dao.query_exists_device_nos()
		self.xls_name = os.path.join( conf_map['xls']['path'], '-'.join( ( self.date, conf_map['xls']['name']) ) )

	def split_log( self, log ):
		''''''
		#如果文件不存在
		if not os.path.exists( log ):
			print log 
			return
		with gzip.open( log ) as log_file:
			details = []
			count = 0
			for line in log_file:
				line_map = {}
				unique_device_map = {}
				line = line.strip()
				if not line:
					continue 
				lines  = line.split( '<|>' ) 
				v_time = lines[0][:16]
				line_map['v_time'] = v_time
				api = lines[0].split('info:')[1].strip()
				line_map['api'] = api
				ip_1 = lines[1]
				line_map['ip_1'] = ip_1
				ip_2 = lines[2]
				line_map['ip_2'] = ip_2
				ip_3 = lines[3]
				line_map['ip_3'] = ip_3
				sversion = lines[5]
				line_map['sversion'] = sversion
				unique_device_map['sversion'] = sversion
				cversion = lines[6]
				line_map['cversion'] = cversion
				unique_device_map['cversion'] = cversion
				useAgent = lines[7]
				line_map['useAgent'] = useAgent
				imei = lines[8]
				line_map['imei'] = imei
				unique_device_map['imei'] = imei
				platform = lines[9]
				line_map['platform'] = platform
				unique_device_map['platform'] = platform
				opertaion = lines[10]
				line_map['opertaion'] = opertaion
				unique_device_map['opertaion'] = opertaion
				deviceid = lines[11]
				line_map['deviceid'] = deviceid
				unique_device_map['deviceid'] = deviceid
				timestamp = lines[12]
				line_map['timestamp'] = timestamp
				network = lines[13]
				line_map['network'] = network
				userid = lines[14]
				line_map['userid'] = userid
				unique_device_map['userid'] = userid
				channel = lines[15]
				line_map['channel'] = channel
				unique_device_map['channel'] = channel
				udid = lines[16]
				line_map['udid'] = udid
				unique_device_map['udid'] = udid
				req_message = lines[18]
				line_map['req_message'] = req_message
				#resp_message = lines[19]
				reqt = lines[20]
				line_map['reqt'] = reqt
				respt = lines[24]
				line_map['respt'] = respt
				self.channels.add( channel )
				if api == REGISTER_RESPONSE:
					json_map = json.loads( respt )
					userid = json_map.get( 'userid' )
					if not userid:
						continue
					channel = json_map.get( 'channel', CHANNEL_OTHER)
					if userid != UNKNOW_VALUE:
						unique_device_map['userid'] = userid
					if channel != UNKNOW_VALUE:
						unique_device_map['channel'] = channel
					self.channel_registers.setdefault( channel, set() ).add( userid )
				elif api == '/v1/initinfo':
					self.channel_boot.setdefault( channel, [] ).append('')
				self.channels.add( channel)
				if self.is_valid_imei( imei ) and  not self.is_device_exists( imei ):
					self.channel_unique_device.setdefault( channel, set() ).add( imei )
					unique_device_map['_id'] = imei
					self.add_unique_device_nos( imei, unique_device_map)
				elif self.is_valid_udid( udid ) and not self.is_device_exists( udid ):
					self.channel_unique_device.setdefault( channel, set() ).add( udid )
					unique_device_map['_id'] = udid
					self.add_unique_device_nos( udid, unique_device_map)
				details.append( line_map )
				count += 1
				if count % 1000 == 0:
					self.save_log_detail( details  )
					details = []
					count = 0
			if count != 0 :
				self.save_log_detail( details )
			

	def art_api_analysis( self ):
		'''api目录有两个或者多个'''
		art2_log = os.path.join( conf_map['log']['path']['api'], '.'.join( (LOG_FILE_NAME,self.date,'gz' ) ) )
		art1_log = os.path.join( conf_map['log']['path1']['api'], '.'.join( (LOG_FILE_NAME,self.date,'gz' ) ) )
		#只统计header信息
		#启动次数
		self.channel_boot ={}
		#所有渠道
		self.channels = set()
		#渠道注册用户
		self.channel_registers = {}
		#渠道设备id，计算新增用户
		self.channel_unique_device = {}
		#唯一设备信息
		self.unique_device_nos = {}
		self.split_log( art2_log )
		self.split_log( art1_log )
		if not self.mongo_dao.query_op_log( 'DETAIL', self.date ):
			self.mongo_dao.add_op_log( 'DETAIL', self.date )

	def save_log_detail( self, details ):
		'''保存明细数据到mongodb'''
		if self.mongo_dao.query_op_log( 'DETAIL', self.date ):
			return
		self.mongo_dao.bulk_add_detail( 'log_detail_' + self.date.replace('-',''), details )
		
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
		self.art_api_analysis()

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
			use_map = {}
			current_row += 1
			channel_name = ALL_CHANNEL.get( channel_no, u'其他')
			new_users = len( self.channel_unique_device.get( channel_no, set() ) )
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
		return ( imei != UNKNOW_VALUE 
				and not imei.startswith('a') 
				and not imei.startswith('h')
				and not imei.startswith('p') 
				and imei != 'msb-web'
				and imei != 'msb-apk'
				and imei != 'msg-iphone' )

	def is_valid_udid( self, udid ):
		'''是否是有效的udid'''
		return ( udid != UNKNOW_VALUE 
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
	log = Art2ApiLog( '2014-12-01')
	log.to_excel()
# 2 save userids
# 3 to excel
# 4 send mail