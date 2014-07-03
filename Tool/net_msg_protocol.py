# !/usr/bin/python
# -*- coding: utf-8-*-
# Filename: net_msg_protocol.py



def formsend(data, cont):
	'''网络协议编码+数据编码
	data: 送信内容
	cont: 命令'''

	return ( '@%4s%s%s' % (len(data)+1, cont, data) )


def netsend(data, cont, sock):
	try:
		sock.send( formsend(data, cont) )
	except:
		raise Exception ('net_msg_protocol.py:netsend exception')


def netrecv(sock):
	'''网络自定义协议处理,读取一条消息.            包头  包体长度  数据协议控制符  数据内容
	包头 + 包体长度 + 包体数据. 例： @00061hello -> @    0006     1              hello
	返回包体内容(包含控制符), 出错返回None.'''

	head = None
	bodylen = ''
	body = ''
	tmp = ''

	try:
		while ( True ):
			# 网络协议控制字符读取
			head = sock.recv(1).decode('utf-8')
			if( head == '@' ):
				# 发现包头, 读取包体长度(4字符)
				bodylen = recvsize(sock, 4)
				if( bodylen == None ):
					return (None)
				# 读取包体内容
				body = recvsize( sock, int(bodylen) )
				break
	except:
		raise Exception ( 'net_msg_protocol.py:netrecv exception' )

	if( body != '' ):
		return (body)
	else:
		return (None)


def recvsize(sock, size):
	'''从sock读取size长度数据.'''

	buf = ''
	tmpbuf = ''
	tmpsize = size

	while (tmpsize > 0) :
		try :
			tmpbuf = sock.recv( tmpsize ).decode('utf-8')
			if( tmpbuf == '' ):
				# 对方退出
				return (None)
			buf += tmpbuf
			tmpsize = size - len(buf)
		except:
			return (None)

	if( buf != '' ):
		return (buf)
	else:
		return (None)
