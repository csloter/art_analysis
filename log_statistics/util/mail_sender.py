# coding:utf-8

'''
Created on 2011-11-2

@author: ericwang
'''
from email import header
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os,traceback
import smtplib
from util import yaml_conf 

#配置信息
conf_map = yaml_conf.conf
smtp_server = conf_map['mail']['smtp_server']
smtp_port = conf_map['mail']['smtp_port']
smtp_user = conf_map['mail']['smtp_user']  
smtp_pass = conf_map['mail']['smtp_pass']


def login():  
    '''  
        发件人登录到服务器  
    '''  
    server = smtplib.SMTP(smtp_server, smtp_port)    
    server.ehlo()    
    server.login(smtp_user, smtp_pass)    
    return server

def sendTextEmail(toAdd, subject, content):  
    '''  
        功能：发送纯文本邮件  
        参数说明：  
        toAdd:收件人E-mail地址    类型：list  
        subject:主题，类型:string  
        content:邮件内容    类型：string  
        fromAdd:发件人，默认为服务器用户  
        返回值：True/False  
    '''  
    result = False  
    server = login()  
    msg = Message()  
    msg['Mime-Version'] = '1.0'    
    msg['From'] = smtp_user    
    msg['To'] = ";".join(toAdd)    
    msg['Subject'] = subject    
#    msg['Date'] = email.Utils.formatdate()          # curr datetime, rfc2822    
    msg.set_payload(content, 'utf-8')
        
    try:        
        server.sendmail(smtp_user, toAdd, str(msg))   # may also raise exc    
        result = True  
    except Exception , ex:    
        print Exception, ex    
        print 'Error - send failed'    
          
    return result  

def send_email_with_html(toAdd, subject, contextHTML):  
    '''  
        功能：发送HTML格式邮件  
        参数说明：  
        toAdd:收件人E-mail地址    类型：list  
        subject:主题，类型:string  
        contentText:文本格式邮件内容    类型：string 
        contextHTML:HTML格式邮件内容    类型：string   
        返回值：True/False  
    '''  
    result = False  
    server = login()  
    msgRoot = MIMEMultipart('related')  
    msgRoot['From'] = smtp_user    
    msgRoot['To'] = ";".join(toAdd)    
    msgRoot['Subject'] = subject    
#    msg['Date'] = email.Utils.formatdate()          # curr datetime, rfc2822    
    #msgRoot.set_payload(content, 'utf-8')
    msgAlternative = MIMEMultipart('alternative') 
    msgRoot.attach(msgAlternative)
    
    #plainText = MIMEText(contentText,'plain','utf-8');#普通文本
    #msgAlternative.attach(plainText)
    
    htmlText = MIMEText(contextHTML,'html','utf-8');#HTML格式文本
    msgAlternative.attach(htmlText)
      
    try:        
        server.sendmail(smtp_user, toAdd, msgRoot.as_string())   # may also raise exc    
        result = True  
    except Exception , ex:    
        print Exception, ex    
        print 'Error - send failed'    
          
    return result

def send_email_attach( to_add, subject, text,files=[] ):  
    '''  
        功能：发送附件邮件  
        参数说明：  
        to_add:收件人E-mail地址    类型：list  
        subject:主题，类型:string
        text:文本内容,类型:string
        files:文件列表,类型list  
        返回值：True/False  
    '''  
    result = False  
    server = login()  
    msgRoot = MIMEMultipart('related')  
    msgRoot['From'] = smtp_user    
    msgRoot['To'] = ";".join(to_add)    
    msgRoot['Subject'] = subject    
    
    msgRoot.attach(MIMEText(text,'html','utf8')) #添加文本
    for xls in files:
        part = MIMEBase('application','octet-stream')
        part.set_payload(open(xls,'rb').read(),'utf8')
        part.add_header('Content-Disposition', 'attachment',filename='%s' % header.Header(os.path.basename(xls),'utf8'))
        #encoders.encode_base64(part) #将http头信息再进行一次编码，否则附件的中文名不能用
        msgRoot.attach(part)
    try:        
        server.sendmail(smtp_user, to_add, msgRoot.as_string())   # may also raise exc    
        result = True  
    except Exception , ex:    
        print Exception, ex
        log.exception('Error - send failed')
        log.exception(traceback.format_exc())
        print 'Error - send failed'    
    #print 'send mail ok' 
    return result


if __name__ == '__main__':
    ''''''
    send_email_attach(['csloter@163.com'], ('邮件测试'), '邮件错误测试',['D:\\test.xls'])
    


