# !/usr/bin/python
# coding: utf-8
# Filename: CControl.py


import socket
import threading

import sys
sys.path.append("..")
from Tool.net_msg_protocol import *
from globals import *
from CSession import *


# 命令类型
COMMAND_HELP 	= '1'
COMMAND_LOGIN 	= '2'
COMMAND_LIST 	= '3'
COMMAND_TO 		= '4'
COMMAND_UC		= '5'
COMMAND_MSG 	= '6'

# 状态
STSTUS_NONE 	= '0'
STATUS_INITED 	= '1'
STATUS_LOGINED 	= '2'

# 输入控制
INPUT_NONE		= '0'
INPUT_SESSIONREQ= '1'


class ClinetControl():
	"""客户端控制类

	登录 发起会话等"""


	_ServerIP = None
	_C_Socket = None
	_ID = None
	_ActSessionPair = None
	_SessionPairList = None
	_InputControl = INPUT_NONE
	_HelpMsg = '-help: show help\r\n-login: login\r\n-list: get remote user list\r\n-to [id]: connect user\r\n-uc [id]: change user\r\n-msg [msg]: send msg to remote user\r\n'
	_Status = STSTUS_NONE

	_REQID = ''


	def __init__(self, sip, csock, id, sessionpairlist):
		self._ServerIP = sip
		self._C_Socket = csock
		self._ID = id
		self._SessionPairList = sessionpairlist
		self._Status = STATUS_INITED


	def ccstart(self):
		'''客户端控制循环开始'''

		if (self._Status != STATUS_INITED):
			return

		self.showhelp()

		try:
			# 用户命令读取线程
			CommandThread = threading.Thread( target = self.inputproc, args = () )
			# 与服务端控制交互线程
			ServerThread = threading.Thread( target = self.contproc, args = () )
			# 线程启动
			CommandThread.start()
			ServerThread.start()
			# 等待线程结束
			CommandThread.join()
			ServerThread.join()
			# 退出
			self.showmsg( "socket close!" )
		except Exception, e:
			G_Log.error( str(e) + " [CControl.py:ccstart]")


	def login(self, id):
		'''登录到服务器'''

		if (self._Status != STATUS_INITED):
			self.showmsg('login fail!')
			return

		try:
			# login send
			if(id != '' or id != None):
				self._ID = id
				self.sendmsg(id, CONT_LOGIN, self._C_Socket)
			else:
				self.sendmsg(self._ID, CONT_LOGIN, self._C_Socket)
		except:
			self.showmsg('login send err!')
			G_Log.error("login err! [CControl.py:login]")


	def loginreact(self, data):
		'''登录的回应处理'''

		if (self._Status != STATUS_INITED):
			return

		if (data == '1'):
			# 登录成功
			self._Status = STATUS_LOGINED
			self.showmsg('login success!')
		else:
			# 登录失败
			self.showmsg('login fail!')


	def userlist(self):
		'''已登录用户列表获取'''

		if (self._Status != STATUS_LOGINED):
			self.showmsg('get user list fail!')
			return

		try:
			# get userlist send
			self.sendmsg('', CONT_USERLIST, self._C_Socket)
		except:
			self.showmsg('userlist send err!')
			G_Log.error("userlist err! [CControl.py:userlist]")


	def userlistreact(self, data):
		'''用户列表获取结果处理'''

		if (self._Status != STATUS_LOGINED):
			self.showmsg('get user list fail!')
			return

		uidlist = data.split( ';' )
		liststr = '' 
		# 登录的用户列表
		for i in range(len(uidlist)):
			liststr += '  '
			liststr += uidlist[i]
			liststr += '\r\n'

		self.showmsg(liststr)


	def userconn(self, oid):
		'''连接到指定用户'''

		if (self._Status != STATUS_LOGINED):
			self.showmsg('connect user fail!')
			return

		try:
			# user connect send
			self.sendmsg(oid, CONT_USERCONN, self._C_Socket)
			# 连接信息加入到会话列表中
			sessionpair = SessionPair(self._ID, oid)
			self._SessionPairList.append(sessionpair)
			self.showmsg('waiting for reply ...')

		except:
			self.showmsg('userconn send err!')
			G_Log.error("userconn err! [CControl.py:userconn]")


	def userconnreact(self, data):
		'''连接方用户同意否结果取得'''

		if (self._Status != STATUS_LOGINED):
			self.showmsg('userconnreact fail!')
			return

		tmp = data.split(';')

		if (tmp[0] == '1'):
			self.showmsg(tmp[1] + ' assent! please wait...')
		else:
			cursor = -1
			for i in range(len(self._SessionPairList)):
				if (self._SessionPairList[i] == tmp[1]):
					cursor = i
					break
			if (cursor != -1):
				self._SessionPairList.remove(self._SessionPairList[cursor])

			self.showmsg(tmp[1] + ' refusal!')


	def userreq(self, data):
		'''客户请求连接的处理-提示'''

		self.showmsg('user: ' + data + '  session request. [yes/no]')
		self._REQID = data
		self._InputControl = INPUT_SESSIONREQ


	def userreqreact(self, data, oid):
		'''客户请求连接的处理-接受或拒绝处理'''

		self._InputControl = INPUT_NONE
		if (data != 'yes'):
			# connect refusal send
			self.sendmsg('0'+';'+oid, CONT_USERREQ, self._C_Socket)
		else:
			# 创建会话对并加入到会话列表中
			sessionpair = SessionPair(self._ID, oid)
			self._SessionPairList.append(sessionpair)
			# connect refusal send
			self.sendmsg('1'+';'+oid, CONT_USERREQ, self._C_Socket)


	def usersession(self, data):
		'''与指定用户会话开始'''

		# data: port;oid;cert
		tmp = data.split(';')
		port = int(tmp[0])

		sessionpair = None
		for i in range(len(self._SessionPairList)):
			if (tmp[1] == self._SessionPairList[i]._OUserID):
				sessionpair = self._SessionPairList[i]
				sessionpair._Cert = tmp[2]
				break

		if (sessionpair == None):
			G_Log.error('sessionpair is none! [CControl.py:usersession]')
			return

		# session 开始
		try:
			sessionpair.start(self._ServerIP, port)
			self._ActSessionPair = sessionpair

		except Exception, e:
			G_Log.error( str(e) + 'sessionpair start fail! [CControl.py:usersession]')
			return


	def userchange(self, oid):
		'''切换当前会话用户'''

		if (self._Status != STATUS_LOGINED):
			self.showmsg('user change fail!')
			return

		for i in range(len(self._SessionPairList)):
			if (oid == self._SessionPairList[i]._OUserID):
				if (self._SessionPairList[i]._Status == True):
					self._ActSessionPair = self._SessionPairList[i]
					self.showmsg('user change OK!')
					return

		self.showmsg('user change fail!')


	def posttouser(self, data):
		'''发送会话消息到对方用户'''

		if (self._Status != STATUS_LOGINED):
			self.showmsg('post to user fail! of status')
			return

		if (self._ActSessionPair == None):
			self.showmsg('post to user fail! of actsessionpair')
			return

		if (self._ActSessionPair._Status == False):
			self.showmsg('post to user fail! of actsessionpair.status')
			return

		try:
			# msg send
			self._ActSessionPair.sessionsend(data)
		except:
			self.showmsg('msg send err!')
			G_Log.error("msg send err! [CControl.py:posttouser]")


	def readmsg(self, sock):
		'''读取服务端控制信息'''

		return (netrecv(sock))


	def sendmsg(self, msg, cont, sock):
		'''发送控制信息到服务端'''

		try:
			netsend(msg, cont, sock)
			return (True)
		except:
			G_Log.error('send control msg to server error! [CControl.py:sendmsg]')
			return (False)


	def inputproc(self):
		'''获取用户命令
		从键盘获取用户输入的消息并加以分发

		-help
		-login
		-list
		-to
		-msg'''

		while (True):
			command, data = self.getinput()

			if ( self._InputControl == INPUT_NONE ):
				if (command == COMMAND_TO):
					self.userconn(data)

				elif (command == COMMAND_UC):
					self.userchange(data)

				elif (command == COMMAND_HELP):
					self.showhelp()

				elif (command == COMMAND_LIST):
					self.userlist()

				elif (command == COMMAND_LOGIN):
					self.login(data)

				elif (command == COMMAND_MSG):
					self.posttouser(data)

			elif (self._InputControl == INPUT_SESSIONREQ):
				self.userreqreact(data, self._REQID)


	def contproc(self):
		'''服务端控制命令获取与分发'''

		while (True):
			msg = self.readmsg(self._C_Socket)

			if (msg[0] == CONT_LOGIN):
				self.loginreact(msg[1:])

			elif (msg[0] == CONT_USERLIST):
				self.userlistreact(msg[1:])

			elif (msg[0] == CONT_USERCONN):
				self.userconnreact(msg[1:])

			elif (msg[0] == CONT_SESSION):
				self.usersession(msg[1:])

			elif (msg[0] == CONT_USERREQ):
				self.userreq(msg[1:])

			elif (msg[0] == CONT_MSG):
				pass


	def showhelp(self):
		'''显示帮助消息'''

		print (self._HelpMsg)


	def showmsg(self, msg):
		'''显示指定消息'''

		print(msg)


	def getinput(self):
		'''获取输入
		从键盘
		返回值： 命令类型， 命令参数'''

		instr = raw_input()

		try:
			if (instr[0] != '-'):
				return (COMMAND_MSG, instr)

			elif (len(instr) >= 3 and instr[:3] == '-to'):
				return (COMMAND_TO, instr[3:].strip())
				# return (COMMAND_TO, instr[1:].replace(' ',''))

			elif (len(instr) >= 3 and instr[:3] == '-uc'):
				return (COMMAND_UC, instr[3:].strip())

			elif (len(instr) >= 4 and instr[:4] == '-msg'):
				return (COMMAND_MSG, instr[4:].lstrip())

			elif (len(instr) >= 5 and instr[:5] == '-help'):
				return (COMMAND_HELP, instr[5:].lstrip())

			elif (len(instr) >= 5 and instr[:5] == '-list'):
				return (COMMAND_LIST, instr[5:].lstrip())

			elif (len(instr) >= 6 and instr[:6] == '-login'):
				return (COMMAND_LOGIN, instr[6:].lstrip())

			else:
				return (COMMAND_MSG, instr)

		except:
			return (COMMAND_MSG, instr)


