import socket
import os
from client import Client
from time import ctime
from files import Files
import sys


BUFSIZE = 1024
serverIp = '127.0.0.1'
serverPort = 50000

#打印提示信息
def help():
	print("键入lss以查看服务器上的所有文件。")
	print("键入lsc以查看本地当前目录的所有文件。")
	print("键入bye以断开与服务器的连接。")
	print("键入get+文件名以从服务器获取相应的文件。")
	print("键入put+文件名以向服务器上传相应的文件。")
	print("键入del+文件名以从服务器删除相应的文件。")

#读取并且分析输入的指令
def read_command(client, files):
	try:
		while True:
			print("键入help以获取帮助")
			print("[%s]"%ctime(), end = '  ')
			command = input("请输入命令:")
			if command == '?' or command == 'help':
				help()
			elif command == 'lss':#列出服务器上的所有文件信息
				client.lss()
			elif command == 'lsc':#列出本地所有文件的信息
				client.lsc(files)
			elif command == 'bye':#断开与服务器的连接
				client.bye()
				sys.exit(0)
			elif command[:3] == 'get':#下载某个文件
				client.get(files, command[3:].strip())
			elif command[:3] == 'put':#上传文件
				client.put(files, command[3:].strip())
			elif command[:3] == 'del':#删除文件
				client.delete(command[3:].strip())
			else:
				print("输入有误。")

	except ConnectionResetError:
		print("[%s] Server :" % (ctime()), end = ' ')
		print("服务器[%s:%s]强迫关闭了一个现有的连接" % (client.server_ip, client.server_port))
		client.client_socket.close()
	except SystemExit:
		print("关闭客户端。")
	except:
		print("发生未知错误导致连接断开。")
		client.client_socket.close()

#建立套接字并连接服务器
def build_connection(server_ip, server_port):
	try:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except:
		print("创建套接字失败！")
		sys.exit(0)
	else:
		try:
			client_socket.connect((server_ip, server_port))
		except:
			print("连接服务器失败！")
			client_socket.close()
			sys.exit(0)
		else:
			print("连接服务器成功！")
			print("服务器%s:%s建立连接。"%(server_ip, str(server_port)))
			return client_socket

	

#开启客户端
def startClient():
	files = Files(os.getcwd()) #建立一个跟当前所在目录有关的文件类
	client_socket = build_connection(serverIp, serverPort)
	client = Client(client_socket, serverIp, serverPort)
	read_command(client, files) #读取命令
	
startClient()
