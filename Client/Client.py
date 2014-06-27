# !/usr/bin/python
# -*-coding: utf-8-*-
# Filename: Socket_Client.py

import socket
import threading


# IP
CONNECT_IP = '192.168.1.55'
# 端口
CONNECT_PORT = 5011
# 超时
CONNECT_TIMEOUT = 2
# 最大读取字节数
RECV_MAXSIZE = 1024


def recv(sock):
	# 信息读取循环
	while True :
		try :
			# 超时设定
			# sock.settimeout( CONNECT_TIMEOUT )
			# 读取 等待数据状态
			buf = sock.recv( RECV_MAXSIZE ).decode('utf-8')

			if buf == 'REMOTE_EXIT' :
				# 客户端退出
				print( 'Client Leave!' )
				break

			if buf == '' :
				# 客户端退出
				print( 'Client Leave!' )
				break

		except socket.error:
			print( 'Client Leave!' )
			break

		except socket.timeout :
			print( 'TimeOut' )
			break

		except :
			print( 'Unknown exception' );
			break

		# 处理
		print ( buf )

def send(sock):
	try :
		while True :
			# 从键盘读入发送信息
			msg = raw_input()
			# 送信
			sock.send( msg.encode( 'utf-8' ) )

	except KeyboardInterrupt :
		# ctrl + c
		print( 'you have Crtl+C, Socket_Send Quit!' )

def start():
	# 地址设定
	Address = ( CONNECT_IP, CONNECT_PORT )
	# socket设定 SOCK_STREAM - TCP
	Socket_Client = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
	# socket连接建立
	if( 0 != Socket_Client.connect_ex( Address ) ):
		print( 'socket connect error!' )
		exit(1)

	# socket送信
	Socket_Client.send( b'Hello Python-Socket! my is client.' )

	try :
		# 读取线程建立
		RecvThread = threading.Thread( target = recv, args = (Socket_Client, ) )
		# 送信线程建立
		SendThread = threading.Thread( target = send, args = (Socket_Client, ) )
		# 读取线程启动
		RecvThread.start()
		# 送信线程启动
		SendThread.start()

		# 等待线程结束
		RecvThread.join()
		SendThread.join()

		# socket关闭
		print( "socket close!" )
		Socket_Client.close()

	except KeyboardInterrupt :
		# ctrl + c
		print( 'you have Crtl+C, Now Quit!' )
		# socket关闭
		Socket_Client.close()
		# Log文件关闭
		ClientLogFile.close()

	# except :
	# 	# socket关闭
	# 	Socket_Client.close()
	# 	# Log文件关闭
	# 	ClientLogFile.close()

	raw_input()

if __name__ == '__main__':
	strat()
