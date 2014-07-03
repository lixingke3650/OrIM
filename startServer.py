# !usr/bin/python
# -*-coding: utf-8-*-
# FileName: startServer.py


from Server import Server

# IP
SERVER_IP = '192.168.1.55'
# 端口
LISTENPORT = 5011
# SessionService Port
SESSIONPORT  = 5013

def main():
	Server.start(SERVER_IP, LISTENPORT, SESSIONPORT)

if __name__ == '__main__':
    main()