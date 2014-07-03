# !usr/bin/python
# -*-coding: utf-8-*-
# FileName: startClient.py


# import Client
from Client import Client


# 客户端ID
USER_ID = '1001'
# IP
# CONNECT_IP = '27.120.120.15'
CONNECT_IP = '192.168.1.55'
# 端口
CONNECT_PORT = 5011

def main():
	Client.start(CONNECT_IP, CONNECT_PORT, USER_ID)

if __name__ == '__main__':
    main()