# -*- coding:utf-8 -*-
'''
Created on 2014-10-28

@author: csloter@163.com
'''
import re
import os.path
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
UNKNOW_VALUE = 'undefined'
#渠道对应关系
ALL_CHANNEL = constants.CHANNELS
#其他渠道
CHANNEL_OTHER = 'other'

class LogAnalysis( object ):
	''''''
	def __init__(self, date):
		'''
		date : %Y-%m-%d
		'''
		self.date = date
		self.mongo_dao = MongoDbDao()
		self.exists_unique_device_nos = self.mongo_dao.query_exists_device_nos()
		self.xls_name = os.path.join( conf_map['xls']['path'], '-'.join( ( self.date, conf_map['xls']['name']) ) )

	def msg_api_log( self ):
		#统计日期，一般是昨天
		log = os.path.join( conf_map['log']['path']['api'], '.'.join( ('meishubao.log',self.date ) ) )
		#只统计header信息
		is_header = False
		#新增用户,需要排除所有已注册用户
		self.channel_new_users = {}
		#启动次数
		self.channel_boot ={}
		#iem udid 与 userid的对应关系
		self.userid_unique_device_no = {}
		#所有渠道
		self.channels = set()

		self.unique_device_nos = {}
		# imei OR udid : channel_no
		users_channel = {}
		details = []
		count = 0
		with open( log ) as log_file:
			for line in log_file:
				#空行
				unique_device_map = {}
				line_map = {}
				line = line.strip()
				if not line:
					continue 
				if line.startswith('@header'):
					is_header = True
					api = line[line.index('/'):]
					continue
				if not is_header:
					continue

				line_arr = line.split( '<|>' )
				if len( line_arr) != 12:
					continue
				v_time = line_arr[0][:16]
				line_map['v_time'] = v_time
				sversion = line_arr[0][16:].split( 'sversion:' )[1]
				unique_device_map['sversion'] = sversion
				line_map['sversion'] = sversion
				cversion = line_arr[1].split( 'cversion:' )[1]
				unique_device_map['cversion'] = cversion
				line_map['cversion'] = cversion
				user_agent = line_arr[2].split( 'userAgent:' )[1]
				line_map['user_agent'] = user_agent
				imei = line_arr[3].split( 'imei:')[1]
				unique_device_map['imei'] = imei
				line_map['imei'] = imei
				platform = line_arr[4].split( 'platform:')[1]
				unique_device_map['platform'] = platform
				line_map['imei'] = imei
				opertaion = line_arr[5].split( 'opertaion:')[1]
				unique_device_map['platform'] = platform
				line_map['imei'] = imei
				deviceid = line_arr[6].split( 'deviceid:')[1]
				unique_device_map['deviceid'] = deviceid
				line_map['deviceid'] = deviceid
				timestamp = line_arr[7].split( 'timestamp:')[1]
				line_map['timestamp'] = timestamp
				network = line_arr[8].split( 'network:')[1]
				line_map['network'] = network
				userid = line_arr[9].split( 'userid:')[1]
				line_map['userid'] = userid
				unique_device_map['userid'] = userid
				channel = line_arr[10].split( 'channel:')[1]
				unique_device_map['channel'] = channel
				line_map['channel'] = channel
				udid = line_arr[11].split( 'udid:')[1]
				unique_device_map['udid'] = udid
				line_map['udid'] = udid

				#print v_time, sversion, cversion, user_agent, imei, platform, opertaion, timestamp, network, userid, channel, udid
				if channel == UNKNOW_VALUE:
					channel = CHANNEL_OTHER
				self.channels.add( channel )
				#启动次数 调用次数
				if api == '/v1/initinfo':
					self.channel_boot.setdefault( channel, [] ).append('')
				
				if userid and userid != UNKNOW_VALUE:
					users_channel[userid] = channel

				if self.is_valid_imei( imei ) and not self.is_device_exists( udid ):
					self.channel_new_users.setdefault( channel, set() ).add( imei )
					self.userid_unique_device_no.setdefault ( userid, set()).add( imei )
					unique_device_map['_id'] = imei
					self.add_unique_device_nos( imei, unique_device_map)
				elif self.is_valid_udid( udid ) and not self.is_device_exists( udid ):
					self.channel_new_users.setdefault( channel, set() ).add( udid )
					self.userid_unique_device_no.setdefault ( userid, set()).add( udid )
					unique_device_map['_id'] = udid
					self.add_unique_device_nos( udid, unique_device_map)
				is_header = False
				details.append( line_map )
				count += 1
				if count % 1000 == 0:
					self.save_log_detail( details  )
					details = []
					count = 0
			if count != 0 :
				self.save_log_detail( details )
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
		self.msg_api_log()

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
			current_row += 1
			channel_name = ALL_CHANNEL.get( channel_no, u'其他')
			new_users = len( self.channel_new_users.get( channel_no, [] ) )
			new_register_users = 0
			channel_boots = len( self.channel_boot.get( channel_no, [] ) ) 
			sheet.write_merge( current_row, current_row , 0, 0, channel_no  )
			sheet.write_merge( current_row, current_row , 1, 1, channel_name )
			sheet.write_merge( current_row, current_row , 2, 3, new_users )
			sheet.write_merge( current_row, current_row , 4, 5, new_register_users )
			sheet.write_merge( current_row, current_row , 6, 7, channel_boots )
			use_map = {}
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
		#to = ( 'zhoufei@meishubao.com', 'liutiefeng@meishubao.com' )
		self.to_excel()
		to = conf_map['mail']['to']
		to_me = conf_map['mail']['to_me']
		subject = self.date + u'日报' 
		text = u'美术宝日报'
		mail_sender.send_email_attach( to, subject, text, [ self.xls_name ])
		mail_sender.send_email_attach( to_me, subject, text, [ self.xls_name ])

	def save( self, values ):
		'''保存数据到db'''
		if not self.mongo_dao.query_op_log( 'API', self.date ):
			self.mongo_dao.add_channel_use( values )
			self.mongo_dao.add_op_log( 'API', self.date )
		for k in self.unique_device_nos:
			self.mongo_dao.upset_unique_device_no( self.unique_device_nos.get( k ) )

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
	log = LogAnalysis( '2014-10-27')
	log.to_excel()
# 2 save userids
# 3 to excel
# 4 send mail