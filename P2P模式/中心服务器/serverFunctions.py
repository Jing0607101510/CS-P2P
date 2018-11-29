from socket import *
from server import Server
from time import ctime
import threading
import sys
from protocol import *


HOST = '127.0.0.1'
PORT = 60000
BUFSIZE = 1024
listen_num = 10

#建立服务器的套接字并绑定
def build_server_sock():
	try:
		server_socket = socket(AF_INET, SOCK_STREAM)
	except:
		print("创建套接字失败！")
		sys.exit()
	else:
		try:
			server_socket.bind((HOST, PORT))
		except:
			print("绑定套接字失败！")
			server_socket.close()
			sys.exit()
		else:
			print("服务器成功创建并绑定套接字！")
			return server_socket


#启动服务器
def startServer():
	server_socket = build_server_sock()
	server = Server(server_socket)
	server.server_socket.listen(listen_num)
	wait_for_connection(server)
	server.server_socket.close()


#多线程：等待连接
def wait_for_connection(server):	
	Id = -1
	while True:
		#try:
		connect_socket, connect_addr = server.server_socket.accept()
		Id += 1
		server.connect_list_addr.append(connect_addr)
		print("与[%s:%s]建立连接。"%connect_addr)
		new_connection = threading.Thread(target = deal_data, args = (server, connect_socket, connect_addr, Id))
		new_connection.start()


#处理客户端发来的命令
def deal_data(server, connect_socket, connect_addr, Id):
		connect_peer = Server(connect_socket)
		try:
			while True:
				req_header = connect_socket.recv(REQ_HEADER_SIZE)
				msgType, command, sourseName, size = struct.unpack(REQ_HEADER_FORM, req_header)
				sourseName = sourseName.decode('utf-8').strip('\0')
				if command == CommandType.BYE:
					print("[%s] Peer%d : 连接已断开！" % (ctime(), Id))
					connect_peer.server_socket.close()
					break
				elif command == CommandType.LSP:
					print("[%s] Peer%d : 请求查看所有peer上所有文件名。" % (ctime(), Id))
					connect_peer.deal_lsp(server)
				elif command == CommandType.ASK:
					print("[%s] Peer%d : 请求查询哪台peer具有给定文件。" % (ctime(), Id))
					connect_peer.deal_ask(server, sourseName)
				elif command == CommandType.PEER:
					print("[%s] Peer%d : 请求获取所有其他peer的信息。" % (ctime(), Id))
					connect_peer.deal_peer(server)

		except ConnectionResetError:
			print("[%s] Peer%d :" % (ctime(), Id), end = ' ')
			print("远程主机[%s:%s]强迫关闭了一个现有的连接" % (connect_addr))
			server.connect_list_addr.remove(connect_addr)
			connect_peer.server_socket.close()
		#except Exception as msg:
			#print(msg)
			#print("发生未知错误导致连接断开。")
			#server.connect_list_addr.remove(connect_addr)
			#connect_peer.server_socket.close()
			

startServer()
