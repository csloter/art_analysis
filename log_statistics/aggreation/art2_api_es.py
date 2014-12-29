# -*- coding:utf-8 -*-
'''
Created on 2014-10-28

@author: csloter@163.com
'''
import re
import os.path
import json
import gzip
import traceback
import logging
import datetime
from logging import handlers
import constants
from util import yaml_conf 
from util import date_util
from db.es import Es

#配置信息
conf_map = yaml_conf.conf
#无效字段
UNKNOW_VALUE = '-'
#用户注册api
REGISTER_RESPONSE = '/v1/userregister'
LOG_PATH=conf_map['es']['log_trace']
es_tracer = logging.getLogger('elasticsearch.trace')
es_tracer.propagate = False
es_tracer.setLevel(logging.ERROR)
es_tracer_handler=logging.handlers.RotatingFileHandler(LOG_PATH,maxBytes=0.5*10**9, backupCount=3)
es_tracer.addHandler(es_tracer_handler)
STATUS_OK = 0
class Art2ApiLogEs( object ):
	''''''
	def __init__(self):
		self.es = Es()

	def split_log( self, log_message ):
		''''''
		try:
			if not log_message:
				return
			line = log_message
			line_map = {}
			line = line.strip()
			if not line:
				return 
			lines  = line.split( '<|>' ) 
			#line_map['v_time'] = date_util.now_utc()
			#v_time = lines[0][:16]
			v_time = lines[0]
			line_map['v_time'] = date_util.timestamp_to_utc_datetime( v_time )
			api = lines[1]
			api = api.replace('/','_')
			line_map['api'] = api
			ip_1 = lines[2]
			line_map['ip_1'] = ip_1
			ip_2 = lines[3]
			line_map['ip_2'] = ip_2
			ip_3 = lines[4]
			line_map['ip_3'] = ip_3
			sversion = lines[6]
			line_map['sversion'] = sversion
			cversion = lines[7]
			line_map['cversion'] = cversion
			useAgent = lines[8]
			imei = lines[9]
			line_map['imei'] = imei
			platform = lines[10]
			line_map['platform'] = platform
			opertaion = lines[11]
			line_map['opertaion'] = opertaion
			deviceid = lines[12]
			line_map['deviceid'] = deviceid
			timestamp = lines[13]
			line_map['timestamp'] = timestamp
			network = lines[14]
			line_map['network'] = network
			userid = lines[15]
			line_map['userid'] = userid
			channel = lines[16]
			line_map['channel'] = channel
			udid = lines[17]
			line_map['udid'] = udid
			req_message = lines[19]
			line_map['req_message'] = req_message
			#resp_message = lines[19]
			reqt = lines[21]
			line_map['reqt'] = reqt
			respt = lines[25]
			line_map['respt'] = respt
			if api == REGISTER_RESPONSE:
				if api == REGISTER_RESPONSE:
					json_map = json.loads( respt )
					userid = json_map.get( 'userid' )
					if not userid or userid == UNKNOW_VALUE:
						return
					channel = json_map.get( 'channel', UNKNOW_VALUE)
					line_map['channel'] = channel
			#没有用用户信息的
			if not userid or userid == UNKNOW_VALUE:
				return
			#操作状态不成功的
			respt = line_map['respt']
			if respt and respt != UNKNOW_VALUE:
				respt_map = json.loads( respt )
				if 'status' in respt_map and respt_map.get('status') != STATUS_OK:
					return
			self.es.index( line_map )
		except:
			 print traceback.format_exc()

	def upload_to_es( self, line_map ):
		'''上传图片'''
		print line_map
		userid = line_map.get('userid')
		es_doc = {}
		if userid and userid != UNKNOW_VALUE:
			es_doc['userid'] = userid
		else:
			return
		channel = line_map.get( 'channel')
		if channel and channel != UNKNOW_VALUE:
			es_doc['channel'] = channel
		#es_doc['online_time'] = date_util.y_m_d_H_M_S_date( line_map['v_time'] )
		#es_doc['upload_time'] = date_util.y_m_d_H_M_S_date( line_map['v_time'] )
		es_doc['online_time'] = line_map['v_time'] 
		es_doc['upload_time'] = line_map['v_time']
		es_doc['v1_uploadaudio'] = line_map
		self.es.index( line_map )

	def just_to_es( self, line_map ):
		'''其他所有接口，只有有操作，说明用户在线'''
		userid = line_map.get('userid')
		es_doc = {}
		if userid and userid != UNKNOW_VALUE:
			es_doc['userid'] = userid
		else:
			return
		channel = line_map.get( 'channel')
		if channel and channel != UNKNOW_VALUE:
			es_doc['channel'] = channel

		#es_doc['online_time'] = date_util.y_m_d_H_M_S_date( line_map['v_time'])
		es_doc['online_time'] = line_map['v_time']
		self.es.index( userid, es_doc )
	
	def follow_to_es( self, line_map):
		'''用户关注'''
		FOLLOW_STATUS_OK = 0
		if not line_map:
			return
		es_doc = {}
		#es_doc_index = {}
		userid = line_map.get('userid')
		if userid and userid != UNKNOW_VALUE:
			es_doc['userid'] = userid
			#es_doc_index['userid'] = userid
		else:
			return
		channel = line_map.get( 'channel')
		if channel and channel != UNKNOW_VALUE:
			es_doc['channel'] = channel
			#es_doc_index['channel'] = channel
		#respt = line_map['respt']
		# if respt and respt != UNKNOW_VALUE:
		# 	respt_map = json.loads( respt )
		# 	if respt_map.get('status') == FOLLOW_STATUS_OK:
		# 		reqt = line_map['reqt']
		# 		if reqt and reqt != UNKNOW_VALUE:
		# 			reqt_map = json.loads( reqt )
		# 			followuserid = reqt_map.get('followuserid')
		# 			follow_script = 'if( !ctx._source.followuserids.contains("'+followuserid+'") ) ctx._source.followuserids.add("' + followuserid + '");'
		# 			es_doc_index['followuserids'] = [followuserid]
		# 			#es_doc['followuserid'] = [followuserid]
		es_doc['online_time'] = line_map['v_time']
		#es_doc_index['online_time'] = date_util.y_m_d_H_M_date( line_map['v_time'])
		self.es.index( userid , es_doc )
		#self.es.upsert( userid, es_doc, es_doc_index, follow_script )

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
		channel = line_map.get( 'channel')
		if channel and channel != UNKNOW_VALUE:
			es_doc['channel'] = channel
		respt = line_map['respt']
		if respt and respt != UNKNOW_VALUE:
			respt_map = json.loads( respt )
			if respt_map.get('status') == UPDATE_USER_STATUS_OK:
				usertype = respt_map.get('usertype')
				if usertype and usertype != UNKNOW_VALUE:
					es_doc['usertype'] = usertype
		es_doc['online_time'] = line_map['v_time']
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
			es_doc['register_date'] =  line_map['v_time']
			es_doc['online_time'] =  line_map['v_time']
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
			es_doc['online_time'] =  line_map['v_time']
			self.es.index( userid, es_doc )


if __name__ == '__main__':
	#log = LogAnalysis( date_util.past_day_Y_m_D_str(1) )
	log = Art2ApiLogEs()
	log_register = '1419862353907<|>/v1/userregister<|>127.0.0.1<|>223.104.21.225<|>-<|>head<|>2.0<|>11<|>msb-apk<|>864085025992153<|>1<|>4.3<|>G620-L75<|>1417449372246<|>0<|>-<|>10100003<|>-<|>req<|>103<|>reqt<|>{"role":"MQ==","passwd":"MTAwODYx","number":"MTM1MTExODcxMjc=","code":"NDMxNDYy","nickname":"5pu+6aKi"}<|>resp<|>418<|>respt<|>{"status":0,"msg":"ok","userid":"547c8fa3c1c30576558cb978","usertype":1,"imei":"864085025992153","channel":"10100003","last_active_time":1417449379320,"nickname":"曾颢","mobile":"13511187127","update_at":"2014-12-01T15:56:19.320Z","create_at":"2014-12-01T15:56:19.320Z","feedcount":0,"followcount":0,"acceptcount":0,"workscount":0,"money":100,"weight":0,"level":1,"is_block":false,"gender":0,"askmecount":0,"platform":1}<|>status<|>0<|>msg<|>ok<|>time<|>9148<|>perf<|>100<|>'
	log_login='1419862353907<|>/v1/userlogin<|>127.0.0.1<|>117.136.31.19<|>-<|>head<|>1.0<|>10<|>msb-apk<|>864837020116927<|>1<|>4.4<|>COOLPAD<|>1417449155293<|>4<|>-<|>10100005<|>-<|>req<|>49<|>reqt<|>{"passwd":"OTYwODI5","number":"MTM1MDE0NTQ3NjY="}<|>resp<|>408<|>respt<|>{"status":0,"msg":"ok","islogin":1,"userid":"547b2cb20bf7da4c5cb8d72c","usertype":2,"sdescription":"nb老师","last_active_time":1417365065944,"nickname":"美院点评","mobile":"13501454766","update_at":"2014-11-30T14:41:54.045Z","create_at":"2014-11-30T14:41:54.045Z","feedcount":0,"followcount":0,"acceptcount":0,"workscount":0,"money":109,"weight":0,"level":1,"is_block":false,"gender":0,"askmecount":0,"platform":1}<|>status<|>0<|>msg<|>ok<|>time<|>595<|>perf<|>100<|>'
	log_updateuser='1419862353907<|>/v1/updateuser<|>127.0.0.1<|>122.4.42.35<|>-<|>head<|>2.0<|>11<|>msb-apk<|>864690025670228<|>1<|>4.4.4<|>MI 3W<|>1417448929920<|>1<|>547800c08f7122db4d1e3dd8<|>10100007<|>-<|>req<|>28<|>reqt<|>{"gender":"2","nickname":""}<|>resp<|>72<|>respt<|>{"status":0,"msg":"ok","userid":"547800c08f7122db4d1e3dd8","usertype":1}<|>status<|>0<|>msg<|>ok<|>time<|>543<|>perf<|>100<|>'
	log_upload='1419862353907<|>/v1/uploadaudio<|>127.0.0.1<|>124.239.208.132<|>-<|>head<|>2.0<|>1.1.6<|>msb-iphone<|>h1417448916<|>2<|>7.1.1<|>iPhone5,2<|>2147483647<|>1<|>547330e9d0d34a6048cfffce<|>-<|>04383B2B-3926-4CB4-BB21-B2016C81FA26<|>req<|>152<|>reqt<|>{"questid":"547bd539d22ff9de6fe1c0bb","duration":"54","audiourl":"http://audiomeishubao.b0.upaiyun.com/2014-12-01/110a2b28b2266e280bb4cc647327cb8f.ogg"}<|>resp<|>131<|>respt<|>{"status":0,"msg":"ok","answerid":"547c8dd4c1c30576558cb7b3","audioid":"547c8dd4c1c30576558cb7b5","create_timestamp":1417448916054}<|>status<|>0<|>msg<|>ok<|>time<|>60<|>perf<|>50<|>'
	log.split_log(log_register)
	log.split_log(log_login)
	log.split_log(log_updateuser)
	log.split_log(log_upload)
# 2 save userids
# 3 to excel
# 4 send mail