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
from logging import handlers
import constants
from util import yaml_conf 
from util import date_util
from db.es import Es

#配置信息
conf_map = yaml_conf.conf
#无效字段
UNKNOW_VALUE = '-'

es_tracer = logging.getLogger('elasticsearch.trace')
es_tracer.propagate = False
es_tracer.setLevel(logging.ERROR)
es_tracer_handler=logging.handlers.RotatingFileHandler(r'd:\top-camps-full.log',
                                                   maxBytes=0.5*10**9,
                                                   backupCount=3)
es_tracer.addHandler(es_tracer_handler)
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
			elif api == '/v1/uploadimg' or api == '/v1/uploadaudio':
				self.upload_to_es( line_map )
			else:
				self.just_to_es( line_map )
		except:
			 print traceback.format_exc()

	def upload_to_es( self, line_map ):
		'''上传图片'''
		userid = line_map.get('userid')
		es_doc = {}
		if userid and userid != UNKNOW_VALUE:
			es_doc['userid'] = userid
		else:
			return
		channel = line_map.get( 'channel')
		if channel and channel != UNKNOW_VALUE:
			es_doc['channel'] = channel
		es_doc['online_time'] = date_util.y_m_d_H_M_date( line_map['v_time'] )
		es_doc['upload_time'] = date_util.y_m_d_H_M_date( line_map['v_time'] )
		self.es.index( userid, es_doc )

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

		es_doc['online_time'] = date_util.y_m_d_H_M_date( line_map['v_time'])
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
		es_doc['online_time'] = date_util.y_m_d_H_M_date( line_map['v_time'])
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
	log = Art2ApiLogEs()
	log.split_log('2014-12-04 23:59 - info: /v1/paintlist/<|>127.0.0.1<|>49.211.60.231<|>-<|>head<|>1.02<|>1.0.1<|>msb-iphone<|>h1417449566<|>2<|>7.1.2<|>iPhone5,2<|>2147483647<|>1<|>547458c77612fbfe662981ab<|>-<|>A7BF1E8E-D17A-42EF-98D7-FDBB287AC0C9<|>req<|>67<|>reqt<|>{"replytype":"0","count":"20","order":"1","questype":"0","pid":"1"}<|>resp<|>11034<|>respt<|>-<|>status<|>0<|>msg<|>ok<|>time<|>561<|>perf<|>100<|>')
# 2 save userids
# 3 to excel
# 4 send mail