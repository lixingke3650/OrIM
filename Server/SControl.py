# !/usr/bin/python
# -*- coding: utf-8-*-
# Filename: SControl.py


import sys
sys.path.append("..")
from Tool.net_msg_protocol import *
from globals import *
from SSession import *

class  UserControl():
	'''用户控制类

	登录 连接 会话等'''

	_User = None
	_S_Socket = None
	_UserList = None
	_SessionManage = None


	def __init__(self, userlist, user, sessionmanage):
		'''ssock: 服务端socket
		user:  客户端结构体'''

		self._UserList = userlist
		self._User = user
		self._SessionManage = sessionmanage


	def servicestart(self):
		'''服务开始
		消息读取 分发'''
		if (self._User == None):
			return

		while (True):
			msg = self.readmsg(self._User._Socket)
			# >>>>
			print( 'server recv msg: ' + msg )
			# <<<<
			if (msg == None):
				G_Log.error('read msg error! [SControl.py:servicestart]')
			self.handproc(msg[0], msg[1:])


	def readmsg(self, sock):
		'''读取客户端控制信息'''

		return (netrecv(sock))


	def sendmsg(self, msg, cont, sock):
		'''发送控制信息到客户端'''

		try:
			netsend(msg, cont, sock)
			return (True)
		except:
			G_Log.error('send control msg to user error! [SControl.py:sendmsg]')
			return (False)


	def handproc(self, cont, data):
		'''消息分发处理'''

		# 客户端登录请求
		if (cont == CONT_LOGIN):
			try:
				self._User._ID = data
				# 注意资源竞争，可引入线程锁(后续)!!
				self._UserList.append( self._User )
			except:
				# 登录失败
				self.sendmsg('0', CONT_LOGIN, self._User._Socket)
				G_Log.error('user add err! [SControl.py:handproc]')

			# 登录成功
			self.sendmsg('1', CONT_LOGIN, self._User._Socket)

		# 客户端P2P请求
		elif (cont == CONT_P2P):
			pass

		# 已登录客户列表请求
		elif (cont == CONT_USERLIST):
			userlist = ''
			if (len(self._UserList) > 0):
				for i in range(len(self._UserList)):
					if ( i != 0 ):
						userlist += ';'
					userlist += self._UserList[i]._ID
			else:
				userlist = ''

			# 格式化送信数据作成
			senddata = formsend(userlist, CONT_USERLIST)
			try:
				self._User._Socket.send(senddata.encode('utf-8'))
			except:
				G_Log.error('userlist send error! [SControl.py:handproc]')

		# 一对一会话连接请求
		elif (cont == CONT_USERCONN):
			tguser = None
			# 连接对象获取
			for i in range(len(self._UserList)):
				if (data == self._UserList[i]._ID):
					tguser = self._UserList[i]
					break
			# 连接请求
			if (tguser != None):
				# 连接请求送信
				self.sendmsg(self._User._ID, CONT_USERREQ, tguser._Socket)

			else:
				self.sendmsg('0'+';'+data, CONT_USERCONN, self._User._Socket)

		# 一对一会话连接请求应答  0;id or 1;id
		elif (cont == CONT_USERREQ):
			tguser = None
			# 应答对象获取
			tmp = data.split(';')
			for i in range(len(self._UserList)):
				if (tmp[1] == self._UserList[i]._ID):
					tguser = self._UserList[i]
					break
			if (tguser != None):
				if (tmp[0] == '1'):
					self.sendmsg('1'+';'+self._User._ID, CONT_USERCONN, tguser._Socket)
					self._SessionManage.sessionstart(tguser, self._User)
				else:
					self.sendmsg('0'+';'+self._User._ID, CONT_USERCONN, tguser._Socket)

		# 会话
		elif (cont == CONT_MSG):
			# 不应通过可控制线路发送会话信息
			G_Log.error('Control recv a session msg! [SControl.py:handproc]')


	def start(self):
		'''用户控制开始'''

		self.servicestart()
