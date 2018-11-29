from socket import *
from time import ctime
from files import Files
import os
from server import Server
import threading
from protocol import *

HOST = "127.0.0.1"
PORT = 50000
BUFSIZE = 1024
ADDR = (HOST, PORT)
listen_num = 5

#建立并绑定套接字
def build_server_sock():
	try:
		server_socket = socket(AF_INET, SOCK_STREAM)
	except:
		print("创建套接字失败！")
		quit()
	else:
		try:
			server_socket.bind(ADDR)
		except:
			print("绑定套接字失败！")
			server_socket.close()
			quit()
		else:
			print("服务器成功创建并绑定套接字！")
			return server_socket


#启动服务器
def startServer():
	server_socket = build_server_sock()
	server = Server(server_socket, HOST, PORT)
	files = Files(os.getcwd())
	server.server_socket.listen(listen_num)
	wait_for_connection(server, files)
	server.server_socket.close()


#多线程：等待连接
def wait_for_connection(server, files):	
	Id = -1
	while True:
		#try:
		connect_socket, connect_addr = server.server_socket.accept()
		Id += 1
		print("与[%s:%s]建立连接。"%connect_addr)
		new_connection = threading.Thread(target = deal_data, args = (connect_socket, connect_addr, files, Id))
		new_connection.start()


#处理客户端发来的命令
def deal_data(connect_socket, connect_addr, files, Id):
		connect_cs = Server(connect_socket)
		try:
			while True:
				req_header = connect_socket.recv(REQ_HEADER_SIZE)
				msgType, command, sourseName, size = struct.unpack(REQ_HEADER_FORM, req_header)
				sourseName = sourseName.decode('utf-8').strip('\0')
				if command == CommandType.BYE:
					print("[%s] Client%d : 连接已断开！" % (ctime(), Id))
					connect_cs.server_socket.close()
					break
				elif command == CommandType.LSS:
					print("[%s] Client%d : 请求查看服务器上所有文件名。" % (ctime(), Id))
					connect_cs.deal_lss(files)
				elif command == CommandType.GET:
					print("[%s] Client%d :" % (ctime(), Id), end = ' ')
					connect_cs.deal_get(files, sourseName)
				elif command == CommandType.PUT:
					print("[%s] Client%d :" % (ctime(), Id), end = ' ')
					connect_cs.deal_put(files, sourseName, size)
				elif command == CommandType.DEL:
					print("[%s] Client%d :" % (ctime(), Id), end = ' ')
					connect_cs.deal_del(files, sourseName)

		except ConnectionResetError:
			print("[%s] Client%d :" % (ctime(), Id), end = ' ')
			print("远程主机[%s:%s]强迫关闭了一个现有的连接" % (connect_addr))
			connect_cs.server_socket.close()
		except:
			print("发生未知错误导致连接断开。")
			connect_cs.server_socket.close()
			

startServer()
