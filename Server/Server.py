# !/usr/bin/python
# -*- coding: utf-8-*-
# Filename: Server.py

import socket
import threading

import sys
sys.path.append("..")
from Tool.net_msg_protocol import *
from globals import *
from SControl import *
from SSession import *


# 最大连接数
CONNECT_MAXNUMBER = 10
# 超时
CONNECT_TIMEOUT = 2
# 最大读取字节数
RECV_MAXSIZE = 1024

# 登录的用户 - 字典[UserID, UserData]
LOGIN_DATA = None

class UserData():
	"""UserData: 用户信息"""

	# ENUM
	STATUS_OFFLINE = -1
	STATUS_ONLINE = 0
	STATUS_STEALTH = 1

	_ID = None
	_IP = None
	_Port = None
	_Status = STATUS_OFFLINE
	_Scoket = None


# service
UserList = []
# sessionpairList
SessionPairList = []
# session port
SessionPort = None

def start(serverip, listenport, sessionport):
	global UserList
	global SessionPort
	global SessionPairList

	SessionPort = sessionport

	# # session socket
	# # socket作成
	# SessionAddress = ( serverip, SessionPort )
	# # 设置socket属性 （通信类型，套接字类型）
	# SessionSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	# # 与IP和端口绑定
	# SessionSocket.bind( SessionAddress )
	# # 开始监听
	# SessionSocket.listen( CONNECT_MAXNUMBER )
	# # session 监听线程
	# sessionthread = threading.Thread( target=sessionlisten, args=(SessionSocket,) )
	# sessionthread.start()

	sessionmanage = SessionManage( serverip, sessionport, SessionPairList )
	sessionmanage.start()

	# server socket
	# socket作成
	ServerAddress = ( serverip, listenport )
	# 设置socket属性 （通信类型，套接字类型）
	ServerSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	# 与IP和端口绑定
	ServerSocket.bind( ServerAddress )
	# 开始监听
	ServerSocket.listen( CONNECT_MAXNUMBER )

	print("OrIM Server Start!")

	# 用户登录等待
	while ( True ):
		ConnectSocket, ClientAddr = ServerSocket.accept()
		usertmp = UserData()
		usertmp._IP = ClientAddr[0]
		usertmp._Port = ClientAddr[1]
		usertmp._Socket = ConnectSocket
		# 客户端控制线程启动
		thread = threading.Thread( target=userstart, args=(usertmp, UserList, sessionmanage) )
		thread.start()


def userstart(user, userlist, sessionmanage):
	uc = UserControl(userlist, user, sessionmanage)
	uc.start()


# def sessionlisten(sock):
# 	# 用户登录等待
# 	while (True):
# 		ConnectSocket, ClientAddr = sock.accept()
# 		sessionproc(ConnectSocket)


# def sessionproc(sock):
# 	'''会话方控制。
# 	会话对若双方都连接成功，则开始会话。'''

# 	global SessionPairList

# 	msg = netrecv(sock)
# 	if (msg[0] != CONT_SESSION):
# 		return

# 	data = msg[1:].split(';')
# 	id = data[0]
# 	cert = data[0]

# 	for i in range(len(SessionPairList)):
# 		if (SessionPairList[i]._User1._ID == id):
# 			if (SessionPairList[i]._Cert != cert):
# 				return
# 			if (SessionPairList[i]._Status == True):
# 				return
# 			SessionPairList[i]._Flag1 = True
# 			if (SessionPairList[i]._Flag2 == True):
# 				sessionconnect(SessionPairList[i])
# 		elif (SessionPairList[i]._User2._ID == id):
# 			if (SessionPairList[i]._Cert != cert):
# 				return
# 			if (SessionPairList[i]._Status == True):
# 				return
# 			SessionPairList[i]._Flag2 = True
# 			if (SessionPairList[i]._Flag1 == True):
# 				sessionconnect(SessionPairList[i])


# def sessionconnect(pair):
# 	'''会话开始'''
# 	csc = CSCService (pair._User1._Socket, pair._User2._Socket)
# 	csc.start()
# 	pair._Status = True


# def sessionstart(user1, user2):
# 	'''一对一会话开始

# 	user1: 请求方   
# 	user2: 被请求方 

# 	1 由服务端分别向双方发送控制信息： 现在可以连接 (包括新连接的端口号和认证信息)
# 	2 服务端开启新端口(服务端启动时即可开启，或者采用动态端口临时开启)等待双方客户端连接
# 	'''
	
# 	global SessionPairList
# 	global SessionPort

# 	# SessionPair
# 	sessp = SessionPair()
# 	sessp._User1 = user1
# 	sessp._User2 = user2
# 	cert = str(random.random(100000, 999999))
# 	sessp._Cert = cert
# 	# 加入到 SessionPairList 
# 	SessionPairList.append(sessp)
# 	# 开始连接消息 port;oid;cert
# 	senddata1 = SessionPort + ';' + sessp._User2._ID + ';' + cert
# 	senddata2 = SessionPort + ';' + sessp._User1._ID + ';' + cert
# 	netsend( senddata1, CONT_SESSION, sessp._User1._Socket )
# 	netsend( senddata2, CONT_SESSION, sessp._User2._Socket )


if __name__ == "__main__":
	# start(SERVER_IP, LISTENPORT)
	pass


