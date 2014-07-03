# !/usr/bin/python
# -*- coding: utf-8-*-
# Filename: CSControl.py

import socket
import threading

import sys
sys.path.append("..")
from Tool.net_msg_protocol import *
from globals import *


class SessionPair():
	'''会话信息'''

	_SessionSocket = None
	_ServerIP = None
	_ServerPort = None
	_UserID = None
	_OUserID = None
	_Cert = None
	_Status = False			# 状态


	def __init__(self, id, oid):
		self._UserID = id
		self._OUserID = oid


	def start(self, serverip, serverport):
		'''客户端会话对开始'''

		if (self._UserID == None or self._OUserID == None or self._Cert == None):
			return

		self._ServerIP = serverip
		self._ServerPort = serverport

		# session socket 连接
		address = (serverip, serverport)
		self._SessionSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		try:
			self._SessionSocket.connect(address)
		except:
			self.showmsg('session socket connect err!')
			G_Log.error('session socket connect err! [CSession.py:usersession]')

		# 通知服务端连接可以开始
		# msg: id;oid;cert
		netsend(self._UserID + ';' + self._OUserID + ';' + self._Cert, CONT_SESSION, self._SessionSocket)
		try:
			# 信息读取线程建立
			sessionrecvthread = threading.Thread( target=self.sessionrecv, args=() )
			sessionrecvthread.start()
		except:
			G_Log.error('sessionrecvthread error! [CSession.py:start]')

		self._Status = True
		print('session start ^_^')


	def sessionrecv(self):
		'''会话消息循环读取'''

		while True :
			try :
				# 超时设定
				# sock.settimeout( CONNECT_TIMEOUT )
				msg = netrecv(self._SessionSocket)
				if(msg == None):
					G_Log.error("sessionrecv msg None. [CSession.py:sessionrecv]")
					return
				self.showmsg(msg)
			except Exception, e:
				G_Log.error(str(e) + 'sessionrecv error! [CSession.py:sessionrecv]')
				return


	def sessionsend(self, msg):
		'''会话消息送信'''

		try:
			netsend(msg, CONT_MSG, self._SessionSocket)
			return (True)
		except:
			G_Log.error('send msg error! [CSession.py:sessionsend]')
			return (False)


	def showmsg(self, data):
		'''收信消息显示'''

		if( data[0] == CONT_MSG ):
			print( data[1:] )
