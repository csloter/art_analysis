# -*- coding:utf-8 -*-
'''
Created on 2014-10-28

@author: csloter@163.com
'''
import re
import os.path
import json
import gzip
import constants
from util import yaml_conf 
from util import date_util
from db.es import Es

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

class Art2ApiLogEs( object ):
	''''''
	def __init__(self, date):
		'''
		date : %Y-%m-%d
		'''
		self.date = date
		self.es = Es()

	def split_log( self ):
		''''''
		art_log = os.path.join( conf_map['log']['path']['api'], '.'.join( (LOG_FILE_NAME,self.date ) ) )
		#如果文件不存在
		if not os.path.exists( art_log ):
			return
		with open( art_log ) as log_file:
			details = []
			count = 0
			for line in log_file:
				line_map = {}
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
				cversion = lines[6]
				line_map['cversion'] = cversion
				useAgent = lines[7]
				imei = lines[8]
				line_map['imei'] = imei
				platform = lines[9]
				line_map['platform'] = platform
				opertaion = lines[10]
				line_map['opertaion'] = opertaion
				deviceid = lines[11]
				line_map['deviceid'] = deviceid
				timestamp = lines[12]
				line_map['timestamp'] = timestamp
				network = lines[13]
				line_map['network'] = network
				userid = lines[14]
				line_map['userid'] = userid
				channel = lines[15]
				line_map['channel'] = channel
				udid = lines[16]
				line_map['udid'] = udid
				req_message = lines[18]
				line_map['req_message'] = req_message
				#resp_message = lines[19]
				reqt = lines[20]
				line_map['reqt'] = reqt
				respt = lines[24]
				line_map['respt'] = respt
				if api == '/v1/userlogin':
					self.login_to_es( line_map )
				elif api == '/v1/userregister':
					self.register_to_es( line_map )
				elif api == '/v1/updateuser':
					self.updateuser_to_es( line_map )
				elif api == '/v1/follow':
					self.follow_to_es( line_map )
	
	def follow_to_es( self, line_map):
		'''用户关注'''
		FOLLOW_STATUS_OK = 0
		if not line_map:
			return
		es_doc = {}
		es_doc_index = {}
		userid = line_map.get('userid')
		if userid and userid != UNKNOW_VALUE:
			es_doc['userid'] = userid
			es_doc_index['userid'] = userid
		else:
			return
		respt = line_map['respt']
		if respt and respt != UNKNOW_VALUE:
			respt_map = json.loads( respt )
			if respt_map.get('status') == FOLLOW_STATUS_OK:
				reqt = line_map['reqt']
				if reqt and reqt != UNKNOW_VALUE:
					reqt_map = json.loads( reqt )
					followuserid = reqt_map.get('followuserid')
					follow_script = 'if( !ctx._source.followuserids.contains("'+followuserid+'") ) ctx._source.followuserids.add("' + followuserid + '");'
					es_doc_index['followuserids'] = [followuserid]
					#es_doc['followuserid'] = [followuserid]
		es_doc['online_time'] = date_util.y_m_d_H_M_date( line_map['v_time'])
		es_doc_index['online_time'] = date_util.y_m_d_H_M_date( line_map['v_time'])
		print follow_script
		print es_doc_index
		self.es.upsert( userid, es_doc, es_doc_index, follow_script )

	def updateuser_to_es( self, line_map ):
		'''用户修改信息添加到es'''
		UPDATE_USER_STATUS_OK = 0
		if not line_map:
			return
		es_doc = {}
		userid = line_map.get('userid')
		if userid and userid != UNKNOW_VALUE:
			es_doc['userid'] = userid
		else:
			return
		respt = line_map['respt']
		if respt and respt != UNKNOW_VALUE:
			respt_map = json.loads( respt )
			if respt_map.get('status') == UPDATE_USER_STATUS_OK:
				usertype = respt_map.get('usertype')
				if usertype and usertype != UNKNOW_VALUE:
					es_doc['usertype'] = usertype
		es_doc['online_time'] = date_util.y_m_d_H_M_date( line_map['v_time'])
		self.es.index( userid, es_doc )

	def register_to_es( self, line_map ):
		'''注册信息添加到es'''
		REGISTER_STATUS_OK = 0
		if not line_map:
			return
		respt =  line_map['respt']
		if not respt or respt == UNKNOW_VALUE:
			return
		respt_map = json.loads( respt )
		if respt_map.get('status') == REGISTER_STATUS_OK:
			es_doc = {}
			userid = respt_map.get('userid')
			if userid and userid != UNKNOW_VALUE:
				es_doc['userid'] = userid
			else:
				return
			nickname = respt_map.get('nickname')
			if nickname:
				es_doc['nickname'] = nickname
			usertype = respt_map.get('usertype')
			if usertype:
				es_doc['usertype'] = usertype
			mobile = respt_map.get('mobile')
			if mobile:
				es_doc['mobile'] = mobile
			gender = respt_map.get('gender')
			if gender is not None:
				es_doc['gender'] = gender
			channel = respt_map.get('channel')
			if channel:
				es_doc['channel'] = channel
			es_doc['register_date'] = date_util.y_m_d_H_M_date( line_map['v_time'])
			es_doc['online_time'] = date_util.y_m_d_H_M_date( line_map['v_time'])
			self.es.index( userid, es_doc )


	def login_to_es( self, line_map ):
		'''登录信息按照需要添加到es中'''
		LOGIN_STATUS_OK = 0
		if not line_map:
			return
		respt =  line_map['respt']
		if not respt or respt == UNKNOW_VALUE:
			return
		respt_map = json.loads( respt )
		if respt_map.get('status') == LOGIN_STATUS_OK:
			es_doc = {}
			userid = respt_map.get('userid')
			if userid and userid != UNKNOW_VALUE:
				es_doc['userid'] = userid
			else:
				return
			nickname = respt_map.get('nickname')
			if nickname:
				es_doc['nickname'] = nickname
			usertype = respt_map.get('usertype')
			if usertype:
				es_doc['usertype'] = usertype
			mobile = respt_map.get('mobile')
			if mobile:
				es_doc['mobile'] = mobile
			gender = respt_map.get('gender')
			if gender is not None:
				es_doc['gender'] = gender
			channel = respt_map.get('channel')
			if channel:
				es_doc['channel'] = channel
			es_doc['online_time'] = date_util.y_m_d_H_M_date( line_map['v_time'])
			self.es.index( userid, es_doc )


if __name__ == '__main__':
	#log = LogAnalysis( date_util.past_day_Y_m_D_str(1) )
	log = Art2ApiLogEs( '2014-12-02' )
	log.split_log()
# 2 save userids
# 3 to excel
# 4 send mail