# !/usr/bin/python
# -*- coding: utf-8-*-
# Filename: Server.py

import socket
import threading

# IP
SERVER_IP = '192.168.1.55'
# 端口
LISTENPORT = 5011
# 最大连接数
CONNECT_MAXNUMBER = 2
# 超时
CONNECT_TIMEOUT = 2
# 最大读取字节数
RECV_MAXSIZE = 1024


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
				sock2.send( sock1.recv( RECV_MAXSIZE ).encode( 'utf-8' ) )
		except:
			print("stop!")

def start():
	# socket作成
	Address = ( SERVER_IP, LISTENPORT )
	# 设置socket属性 （通信类型，套接字类型）
	ServerSocket = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	# 与IP和端口绑定
	ServerSocket.bind( Address )
	# 开始监听
	ServerSocket.listen( CONNECT_MAXNUMBER )

	print("ORIM Server Start!")
	count = 0
	Socket1 = None;
	Socket2 = None;

	while (count < 2):
		# 等待连接
		ConnectSocket, ClientAddr = ServerSocket.accept()
		if( count == 0 ):
			print( "1 : " ),
			print( ClientAddr )
			Socket1 = ConnectSocket
			count += 1
			continue
		if( count == 1 ):
			print( "2 : " ),
			print( ClientAddr )
			Socket2 = ConnectSocket
			csc = CSCService (Socket1,Socket2)
			csc.start()
			count += 1


if __name__ == "__main__":
	start()