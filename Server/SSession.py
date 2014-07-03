# !/usr/bin/python
# -*- coding: utf-8-*-
# Filename: SSession.py

import socket
import threading
import random
import sys
sys.path.append("..")
from Tool.net_msg_protocol import *
from globals import *


# 最大连接数
CONNECT_MAXNUMBER = 10
# 超时
CONNECT_TIMEOUT = 2
# 最大读取字节数
RECV_MAXSIZE = 1024


class SessionPair():
	'''会话信息'''

	_User1 = None
	_User2 = None
	_Socket1 = None
	_Socket2 = None
	_Cert = None
	_Flag1 = False
	_Flag2 = False
	_Status = False


class CSCService(object):
	"""CSCService: 
	维持 "Client to Service to Client" 数据流。"""

	_IsStart = False;
	_Thread1To2 = None
	_Thread2To1 = None

	def __init__(self, sock1, sock2):
		self._Thread1To2 = threading.Thread( target=self.course, args=(sock1,sock2) )
		self._Thread2To1 = threading.Thread( target=self.course, args=(sock2,sock1) )

	def start(self):
		self._IsStart = True
		self._Thread1To2.start()
		self._Thread2To1.start()

	def stop(self):
		self._IsStart = False
		self._Thread1To2.join()
		self._Thread2To1.join()

	def course(self, sock1, sock2):
		'''从sock1读取，向sock2发送'''

		try:
			while (self._IsStart == True):
				msg = sock1.recv( RECV_MAXSIZE ).encode( 'utf-8' )
				print(msg)
				sock2.send( msg )
				# sock2.send( sock1.recv( RECV_MAXSIZE ).encode( 'utf-8' ) )
		except:
			print("stop!")

class P2PServer():
	'''P2P 方式通信

	首先尝试 user2 直接连接 user1(假设user1处于外网),
	其次尝试 user1 直接连接 user2(假设user2处于外网),
	再次尝试 NAT穿透.'''

	# 连接等待方
	_User1 = None
	# 连接发起方
	_User2 = None

	def __init__(self, user1, user2):
		'''构造.
		user1 <- user2 方向连接.
		'''

		self._User1 = user1
		self._User2 = user2

	def start():
		'''P2P通信开始, 
		失败返回False.'''


class SessionManage():
	'''一对一会话管理器'''

	_SessionPairList = None
	_ServerIP = None
	_ServerPort = None
	_ThreadLock = None

	def __init__(self, serverip, serverport, sessionpairlist):
		self._SessionPairList = sessionpairlist
		self._ServerPort = serverport
		self._ServerIP = serverip
		# self._ThreadLock = threading.allocate_lock()

	def start(self):
		# session socket
		# socket作成
		SessionAddress = ( self._ServerIP, self._ServerPort )
		# 设置socket属性 （通信类型，套接字类型）
		SessionSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		# 与IP和端口绑定
		SessionSocket.bind( SessionAddress )
		# 开始监听
		SessionSocket.listen( CONNECT_MAXNUMBER )
		# session 监听线程
		sessionlistenthread = threading.Thread( target=self.sessionlisten, args=(SessionSocket,) )
		sessionlistenthread.start()

		print('sessionmanage service start!')


	def sessionlisten(self, sock):
		# 用户登录等待
		try:
			while (True):
				ConnectSocket, ClientAddr = sock.accept()
				# session thread start
				sessionthread = threading.Thread( target=self.sessionproc, args=(ConnectSocket,) )
				sessionthread.start()

		except:
			G_Log.error('session socket accept error! [SSession.py:sessionlisten]')


	def sessionproc(self, sock):
		'''会话方控制。
		会话对若双方都连接成功，则开始会话。'''

		msg = netrecv(sock)
		if (msg[0] != CONT_SESSION):
			return

		# msg: id;oid;cert
		data = msg[1:].split(';')
		id = data[0]
		oid = data[1]
		cert = data[2]

		for i in range(len(self._SessionPairList)):
			if (self._SessionPairList[i]._User1._ID == id):
				if (self._SessionPairList[i]._User2._ID != oid):
					return
				if (self._SessionPairList[i]._Cert != cert):
					return
				if (self._SessionPairList[i]._Status == True):
					return
				self._SessionPairList[i]._Socket1 = sock
				self._SessionPairList[i]._Flag1 = True
				if (self._SessionPairList[i]._Flag2 == True):
					self.sessionconnect(self._SessionPairList[i])
			elif (self._SessionPairList[i]._User2._ID == id):
				if (self._SessionPairList[i]._User1._ID != oid):
					return
				if (self._SessionPairList[i]._Cert != cert):
					return
				if (self._SessionPairList[i]._Status == True):
					return
				self._SessionPairList[i]._Socket2 = sock
				self._SessionPairList[i]._Flag2 = True
				if (self._SessionPairList[i]._Flag1 == True):
					self.sessionconnect(self._SessionPairList[i])


	def sessionconnect(self, pair):
		'''会话开始'''

		print('sessionconnect!')
		try:
			csc = CSCService(pair._Socket1, pair._Socket2)
			pair._Status = True
			csc.start()
		except:
			G_Log.error('sessionconnect error! [SSession.py:sessionconnect]')


	def sessionstart(self, user1, user2):
		'''一对一会话开始

		user1: 请求方   
		user2: 被请求方 

		1 由服务端分别向双方发送控制信息： 现在可以连接 (包括新连接的端口号和认证信息)
		2 服务端开启新端口(服务端启动时即可开启，或者采用动态端口临时开启)等待双方客户端连接
		'''

		# SessionPair
		sessp = SessionPair()
		sessp._User1 = user1
		sessp._User2 = user2
		cert = str(random.randint(100000, 999999))
		sessp._Cert = cert
		# 加入到 SessionPairList 
		self._SessionPairList.append(sessp)
		# 开始连接消息 port;oid;cert
		senddata1 = str(self._ServerPort) + ';' + sessp._User2._ID + ';' + cert
		senddata2 = str(self._ServerPort) + ';' + sessp._User1._ID + ';' + cert
		netsend( senddata1, CONT_SESSION, sessp._User1._Socket )
		netsend( senddata2, CONT_SESSION, sessp._User2._Socket )