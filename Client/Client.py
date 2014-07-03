# !/usr/bin/python
# -*-coding: utf-8-*-
# Filename: Socket_Client.py

'''信息收发协议: 
网络协议: 包体 + 包体长度 + 包体数据
数据协议: 控制(1字符) + 数据'''


import socket
import threading

import sys
sys.path.append("..")
from Tool.net_msg_protocol import *
from globals import G_Log
from CControl import *
from CSession import *


# # IP
# CONNECT_IP = '192.168.1.55'
# # 端口
# CONNECT_PORT = 5011
# # 超时
# CONNECT_TIMEOUT = 2
# # 最大读取字节数
# RECV_MAXSIZE = 1024

SEQ_NONE = 0
SEQ_LOGIN = 1
SEQ_USERLIST = 2
SEQ_USERCONN = 3
SEQ_SESSION = 4

# Client ID
USER_ID = None
# SessionPair List
SessionPairList = []


def start(connectip, connectport, id):
	global USER_ID
	global SessionPairList

	USER_ID = id

	try:
		# 地址设定
		Address = ( connectip, connectport )
		# socket设定 SOCK_STREAM - TCP
		Socket_Client = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
		# socket连接建立
		Socket_Client.connect( Address )

		# CControl Create
		ccontrol = ClinetControl( connectip, Socket_Client, USER_ID, SessionPairList )
		# CControl start
		ccontrol.ccstart()

	except Exception, e:
		G_Log.error( str(e) + " [Client.py:start]")


if __name__ == '__main__':
	# start(CONNECT_IP, CONNECT_PORT)
	pass
