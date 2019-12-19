# -*- coding:utf-8 -*-

from urllib import request,parse
from hashlib import md5
import urllib.request
import http.cookiejar
import json
import threading
import time,datetime
import sys,os
#Classes
class NoRedirHandler(request.HTTPRedirectHandler):
    def http_error_302(self,req,fp,code,msg,headers):
        return fp
    http_error_301=http_error_302
    
#Global Variables
g_loginstate=False;
g_mousePath='XDAABXAQBrXAgBzXAwB4XBQB7XBwB/XCgCDXDACHXEACLXEgCPXFQCTXGQCXXHACcXHwCfXIgCjXJQCnXLACrXNgCvXQACzXSwC3YUgC7YWAC/ZXADDZYgDHaaQDLabQDOacwDTaeADXafADbagQDfahADjaiQDnajADrajwDvakgDyalQD3amAD7amQD/amgEDamwEHanAELanQEPangEXanwEbaoAG2aoQG7aogG+aowHDbpgHHbqQHLbqwHPbrgHVbsgHXctQHbctwHhdugHjdvgHndwgHrdwwHvdxwHzdygH3dzQH7d0AH/d0wIDd1wIHd2QILd2wIPd3QITd3gIXd3wIfd4ALJd4QLTd4gLbd4gLfd4wLvd5ALzd5QL9d5gMDGrAIC'
g_loginurl='https://uims.jlu.edu.cn/ntms/j_spring_security_check'
g_resurl='https://uims.jlu.edu.cn/ntms/service/res.do'
g_chooselessonurl='https://uims.jlu.edu.cn/ntms/action/select/select-lesson.do'
g_userinfourl='https://uims.jlu.edu.cn/ntms/action/getCurrentUserInfo.do'
g_headers={
  'User-Agent':'Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36',
  'Origin':'https://uims.jlu.edu.cn',
  'Host': 'uims.jlu.edu.cn',
  'referer': 'https://uims.jlu.edu.cn/ntms/userLogin.jsp?reason=logout',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Connection': 'Keep-Alive',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
  'Upgrade-Insecure-Requests': '1'
}
g_json_headers={
  'User-Agent':'Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36',
  'Origin':'https://uims.jlu.edu.cn',
  'Host': 'uims.jlu.edu.cn',
  'referer': 'https://uims.jlu.edu.cn/ntms/userLogin.jsp?reason=logout',
  'Content-Type': 'application/json',
  'Connection': 'Keep-Alive',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
  'Upgrade-Insecure-Requests': '1'
}
g_cookies=http.cookiejar.CookieJar()
g_cookiehandler=urllib.request.HTTPCookieProcessor(g_cookies)
g_opener=urllib.request.build_opener(g_cookiehandler,NoRedirHandler)
g_chosenlist=[];
g_userid=0
g_times=1
g_starttime=""
g_starttimestamp=4099356315
#Personal Information
stu_account='0'
stu_password='0'
#Functions
def getTransferMd5(stu_account,stu_password):
  return md5(('UIMS' + stu_account + stu_password).encode('utf-8')).hexdigest()
def login(username,password_md5,timeout):
    global g_loginstate
    login_data={
    'j_username':username,
    'j_password':password_md5,
    'mousePath':g_mousePath,
    } 
    login_data = parse.urlencode(login_data).encode('utf-8')
    request_login=request.Request(url=g_loginurl,data=login_data,headers=g_headers,method='POST')
    response_login=g_opener.open(request_login,timeout=timeout)
    login_msg=response_login.getheader('Location')
    if 'https://uims.jlu.edu.cn/ntms/index.do' in login_msg:
      print("Login Successfully!\n")
      g_loginstate=True;
    else:
      print("Login Failed!\n")
      g_loginstate=False;
    return
def getlessons_quick(timeout):
    global g_chosenlist
    if g_chosenlist!=None:
       g_chosenlist=[];
    request_data='{"tag":"lessonSelectLogTcm@selectGlobalStore","branch":"quick","params":{"splanId":10}}'
    request_data=bytes(request_data,encoding='utf-8')
    request_getlessons=request.Request(url=g_resurl,data=request_data,headers=g_json_headers,method='POST')
    response_getlessons=g_opener.open(request_getlessons,timeout=timeout)
    response_lessons=response_getlessons.read().decode('utf-8')
    json_lessons=json.loads(response_lessons)
    lessons_nums=len(json_lessons['value'])
    print('当前快捷选课数量:'+str(lessons_nums)+"\n")
    for item in json_lessons['value']:
      g_chosenlist.append(str(item['lsltId']))
      #print(item['lessonSegment']['fullName']+" :\n"+item['lsltId']+"\n")
      print(item['lessonSegment']['fullName']+" : "+item['teachClassMaster']['lessonTeachers'][0]['teacher']['name']+"-"+item['teachClassMaster']['lessonSchedules'][0]['classroom']['fullName']+"\n")
   # for item in g_chosenlist:
     # print(item)
def getlessons_choosetime(timeout):
    global g_starttime
    global g_starttimestamp
    global g_userid
    request_data='{"type":"query","res":"query-splan-by-stud","params":{"studId":'+str(g_userid)+'}}'
    request_data=bytes(request_data,encoding='utf-8')
    request_getchoosetime=request.Request(url=g_resurl,data=request_data,headers=g_json_headers,method='POST')
    response_getchoosetime=g_opener.open(request_getchoosetime,timeout=timeout)
    json_choosetime=json.loads(response_getchoosetime.read().decode('utf-8'))
    print("您当前的选课计划: "+json_choosetime['value'][0]['title']+'\n')
    g_starttime=json_choosetime['value'][0]['currStartTime'].replace('T',' ');
    print("开始时间: "+json_choosetime['value'][0]['currStartTime'].replace('T',' '))
    print("结束时间: "+json_choosetime['value'][0]['currStopTime'].replace('T',' ')+'\n')
    g_starttimestamp=time.mktime(time.strptime(g_starttime, '%Y-%m-%d %H:%M:%S'))
    print("当前时间: "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"\n")
def getuserinfo(timeout):
    global g_userid;
    request_getuserinfo=request.Request(url=g_userinfourl,headers=g_headers,method='POST')
    response_getuserinfo=g_opener.open(request_getuserinfo,timeout=timeout)
    json_userinfo=json.loads(response_getuserinfo.read().decode('utf-8'))
    g_userid=json_userinfo['userId']
    print("欢迎您,"+json_userinfo['nickName']+"\n")
def select_lessons(timeout):
    global g_chosenlist
    i=0
    for item in g_chosenlist:
      i=i+1
      print("当前进行第 "+str(i)+" 项选课\n")
      request_data='{"lsltId":"'+str(item)+'","opType":"Y"}'
      request_data=bytes(request_data,encoding='utf-8')
      request_select=request.Request(url=g_chooselessonurl,data=request_data,headers=g_json_headers,method='POST')
      response_select=g_opener.open(request_select,timeout=timeout)
      json_select=json.loads(response_select.read().decode('utf-8'))
      state=json_select['status']
      if state>=0:
        print("成功 : "+json_select['msg']+'\n')
      else:
        print("失败 : "+json_select['msg']+'\n')
if __name__ == "__main__":
  stu_account=input("请输入学号: ")
  stu_password=input("请输入密码: ")
  stu_password_md5=getTransferMd5(stu_account,stu_password)
  os.system('cls')
  login(stu_account,stu_password_md5,15)
  if g_loginstate==False:
      print("请检查密码后重新输入")
      sys.exit()
  getuserinfo(15)
  getlessons_quick(15)
  getlessons_choosetime(15)
  print("Keep Alive Start!心跳包开始发送！\n")
  while True:
    nowtime=int(time.time())
   # print(nowtime)
    if g_times%60==0:
      print("当前时间: "+datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+"\n")
      login(stu_account,stu_password_md5,15)
    if g_loginstate==False:
      print("登录失败，正在尝试重新登录...")
     # login(stu_account,stu_password_md5,10)
    if nowtime>=g_starttimestamp:
      print("到达选课时间,开始选课\n")
      select_lessons(15)
      break
      
    time.sleep(1)
    g_times=g_times+1