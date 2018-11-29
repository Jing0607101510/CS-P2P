from socket import *
from time import ctime
import os
from files import Files
import struct
import sys
from protocol import *


BUFSIZE = 1024


class Server:
	def __init__(self, server_socket, server_ip = '', server_port = 0):
		self.server_socket = server_socket
		self.server_ip = server_ip
		self.server_port = server_port

	#处理列取服务器所有文件信息的请求
	def deal_lss(self, files):
		files.update_files()
		files_list = files.list_files()

		file_info = ''
		for file in files_list:
			file_info += file + ' : ' + str(os.stat(file).st_size) + '//'
		file_info = file_info.encode('utf-8')

		res_protocol = Res_Protocol(StateCode.OK, len(file_info))
		res_header = res_protocol.make_packet_header()
		self.server_socket.sendall(res_header)

		self.server_socket.sendall(file_info)

		print("成功")



	#处理客户端的下载请求
	def deal_get(self, files, file_name):
		files.update_files()
		print('请求下载服务器上%s文件。' % file_name)

		if file_name in files.files_list:
			
			file_size = os.stat(file_name).st_size
			res_protocol = Res_Protocol(StateCode.OK, file_size)
			res_header = res_protocol.make_packet_header()
			self.server_socket.sendall(res_header)

			#传输文件
			with open(file_name, 'rb') as file:
				while True:
					data = file.read(BUFSIZE)
					if not data:
						print("%s文件传输完成!"%file_name)
						break
					self.server_socket.send(data)

		else:
			res_protocol = Res_Protocol(StateCode.NOTFOUND)
			res_header = res_protocol.make_packet_header()
			self.server_socket.sendall(res_header)



	#处理客户端的上传请求
	def deal_put(self, files, file_name, file_size):
		files.update_files()
			#获取文件名和大小
		
		print('请求上传到服务器上%s文件。' % file_name)
		

		while file_name in files.files_list:
			file_name = 'new_' + file_name
		print('上传后文件名为：' + file_name)

		#接受文件
		recvd_size = 0
		with open(file_name, 'wb') as newfile:
			print("开始接收...")

			while recvd_size != file_size:
				if file_size - recvd_size > BUFSIZE:
					data = self.server_socket.recv(BUFSIZE)
					recvd_size += len(data)
				else:
					data = self.server_socket.recv(file_size - recvd_size)
					recvd_size += len(data)
				newfile.write(data)

		res_protocol = Res_Protocol(StateCode.OK)
		res_header = res_protocol.make_packet_header()
		self.server_socket.sendall(res_header)
		print("接收完成！")
		files.update_files()




	#处理客户端的删除请求
	def deal_del(self, files, file_name):
		files.update_files()

		print('请求删除服务器上%s文件。' % file_name)
		print("正在删除")
		
		#检查服务器上是否有该文件
		if file_name in files.files_list:
			files.del_files(file_name)

			res_protocol = Res_Protocol(StateCode.OK)
			res_header = res_protocol.make_packet_header()
			self.server_socket.sendall(res_header)
			print("删除成功！")
		else:
			res_protocol = Res_Protocol(StateCode.FAIL)
			res_header = res_protocol.make_packet_header()
			self.server_socket.sendall(res_header)
			print("删除失败！")



