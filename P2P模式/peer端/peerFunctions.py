import socket
import threading
from peer import Client_For_Peer
from peer import Server_For_Peer
from files import Files
import os
from time import ctime
import sys
from protocol import *

BUFSIZE = 1024
serverIp = '127.0.0.1'
serverPort = 60000


#与中心服务器进行连接
def build_connection(server_ip, server_port):
	try:
		client_socket_for_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		print("创建与远程服务器的连接套接字失败！")
		sys.exit()
	else:
		try:
			client_socket_for_peer.connect((server_ip, server_port))
		except:
			print("连接远程服务器失败！")
			client_socket_for_peer.close()
			sys.exit()
		else:
			print("连接远程服务器[%s:%s]成功！" % (server_ip, server_port))
			return client_socket_for_peer


#建立监听套接字，监听是否有其他peer连接
def build_server_socket(host_ip, host_port, peer_client):
	try:
		server_socket_for_peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except Exception as e:
		print(e)
		print("创建与peer连接套接字失败！")
		peer_client.client_socket.close()
		sys.exit()
	else:
		try:
			server_socket_for_peer.bind((host_ip, host_port))
		except:
			print("绑定与peer连接的套接字失败！")
			server_socket_for_peer.close()
			peer_client.client_socket.close()
			sys.exit()
		else:
			print("监听连接到本地的套接字创建成功！")
			return server_socket_for_peer

#打印帮助信息
def help():
	print("键入lsp以查看所有peer上的所有文件信息。")
	print("键入lsc以查看本地当前目录的所有文件。")
	print("键入bye以断开与服务器的连接。")
	print("键入get+文件名以从其他peer处获取相应的文件。")
	print("键入ask+文件名以向服务器询问谁有所要的文件。")
	print("键入peer以获取所有已登录的所有peer的信息。")


#读取用户输入的指令并分析
def read_command(peer_client, files):
	try:
		while True:
			print("键入help以获取帮助")
			print("[%s]"%ctime(), end = '  ')
			command = input("请输入命令:")
			command = command.split(' ')
			command[0] = command[0].strip()
			if command[0] == '?' or command[0] == 'help':
				help()
			elif command[0] == 'lsp':#列出所有peer上的所有文件信息
				peer_client.lsp()
			elif command[0] == 'lsc':#列出本地所有文件的信息
				peer_client.lsc(files)
			elif command[0] == 'bye':#断开与服务器的连接
				peer_client.bye()
				sys.exit()
			elif command[0] == 'get':#下载某个文件
				if len(command) == 2:
					peer_client.get(files, command[1].strip())
			elif command[0] == 'ask':#查询哪台peer具有给定文件
				if len(command) == 2:
					peer_client.ask(command[1].strip())
			elif command[0] == 'peer':
				peer_client.peer()
			else:
				print("输入有误。")

	except ConnectionResetError:
		print("[%s] Server :" % (ctime()), end = ' ')
		print("服务器[%s:%s]强迫关闭了一个现有的连接" % (peer_client.server_ip, peer_client.server_port))
		peer_client.client_socket.close()
	#except Exception as msg:
		#print(msg)
		#print("发生未知错误导致连接断开。")
		#peer_client.client_socket.close() 



#建立本地服务端，相应相应的连接
def wait_for_connection(peer_server, files):	
	while True:
		#try:
		connect_socket, connect_addr = peer_server.server_socket.accept()
		print("与[%s:%s]建立连接。"%connect_addr)
		new_connection = threading.Thread(target = deal_data, args = (connect_socket , connect_addr, files))
		new_connection.start()




#根据其他peer传入的指令，执行相应操作
def deal_data(connect_socket, connect_addr, files):
		connect_cs = Server_For_Peer(connect_socket)
		try:
			req_header = connect_socket.recv(REQ_HEADER_SIZE)
			msgType, command, sourseName, size = struct.unpack(REQ_HEADER_FORM, req_header)
			sourseName = sourseName.decode('utf-8').strip('\0')
			if command == CommandType.BYE:
				print("[%s] "%ctime(), end = ' ')
				print("Peer[%s : %s] : 连接已断开！"%connect_addr)
				connect_cs.server_socket.close()
			elif command == CommandType.LSP:
				print("[%s] "%ctime(), end = ' ')
				print("Peer[%s : %s] : 请求查看本地上所有文件名。"%connect_addr)
				connect_cs.deal_lsp(files)
			elif command  == CommandType.GET:
				print("[%s] "%ctime(), end = ' ')
				print("Peer[%s : %s] : 请求下载部分文件。"%connect_addr)
				connect_cs.deal_get(files, sourseName)
			elif command == CommandType.ASK:
				print("[%s] "%ctime(), end = ' ')
				print("Peer[%s : %s] : 请求询问是否有某个文件。"%connect_addr)
				connect_cs.deal_ask(files, sourseName)
				

		except ConnectionResetError:
			print("[%s] Client%d :" % (ctime(), Id), end = ' ')
			print("远程主机[%s:%s]强迫关闭了一个现有的连接" % (connect_addr))
			connect_cs.server_socket.close()
		connect_cs.server_socket.close()
		#except Exception as msg:
			#print(msg)
			#print("发生未知错误导致连接断开。")
			#connect_cs.server_socket.close()




#运行peer端
def startPeer():
	files = Files(os.getcwd())
	client_socket_for_peer = build_connection(serverIp, serverPort)
	peer_client = Client_For_Peer(client_socket_for_peer, serverIp, serverPort)

	host_ip, host_port = peer_client.client_socket.getsockname()
	server_socket_for_peer = build_server_socket(host_ip, host_port, peer_client)
	peer_server = Server_For_Peer(server_socket_for_peer)
	peer_server.server_socket.listen(5)

	As_client = threading.Thread(target = read_command, args = (peer_client, files))
	As_client.start()

	As_server = threading.Thread(target = wait_for_connection, args = (peer_server, files))
	As_server.start()
	#peer_client.client_socket.close()
	#peer_server.server_socket.close()

startPeer()



