import socket
import os
import sys
from files import Files
import struct
from protocol import *

BUFSIZE = 1024



class Client:
	def __init__(self, client_socket, server_ip, server_port):
		self.client_socket = client_socket
		self.server_ip = server_ip
		self.server_port = server_port


	#列出服务器上的所有文件
	def lss(self):
		req_protocol = Req_Protocol(CommandType.LSS)
		req_header = req_protocol.make_packet_header()
		self.client_socket.sendall(req_header)

		res_header = self.client_socket.recv(RES_HEADER_SIZE)
		msgType, stateCode, size = struct.unpack(RES_HEADER_FORM, res_header)

		print("服务器所有文件如下：")
		recvd_size = 0
		file_info = ''
		while recvd_size != size:
			if size - recvd_size > BUFSIZE:
				data = self.client_socket.recv(BUFSIZE)
				recvd_size += len(data)
			else:
				data = self.client_socket.recv(size - recvd_size)
				recvd_size += len(data)
			file_info += data.decode('utf-8')

		files = file_info.split('//')
		while '' in files:
			files.remove('')

		count = 0
		for file in files:
			count += 1
			file_name, file_size = file.split(' : ')
			print("%s     %sbytes"%(file_name, file_size))
		print("服务器上一个有%s个文件。"%count) 



	#列出所在目录下的所有文件OK
	def lsc(self, files):
		files.update_files()
		files_list = files.list_files()
		print("本地的所有文件如下：")
		for file in files_list:
			print("%s     %sbytes" % (file, os.stat(file).st_size))
		print("共%d个文件。"%len(files_list))


	#下载文件
	def get(self, files, file_name):
		files.update_files()
		req_protocol = Req_Protocol(CommandType.GET, file_name)
		req_header = req_protocol.make_packet_header()
		self.client_socket.sendall(req_header)

		res_header = self.client_socket.recv(RES_HEADER_SIZE)
		msgTyep, stateCode, file_size = struct.unpack(RES_HEADER_FORM, res_header)

		if stateCode == StateCode.OK:

			print('服务器上的文件名为：' + file_name)

			while file_name in files.files_list:
				file_name = 'new_' + file_name

				#接收文件
			recvd_size = 0
			with open(file_name, 'wb') as newfile:
				print("开始接收...")

				while recvd_size != file_size:
					if file_size - recvd_size > BUFSIZE:
						data = self.client_socket.recv(BUFSIZE)
						recvd_size += len(data)
					else:
						data = self.client_socket.recv(file_size - recvd_size)
						recvd_size += len(data)
					newfile.write(data)
			print("接收完成！")
			print('在本地的文件名为：' + file_name)
			files.update_files()

		else:
			print("服务器上不存在此文件！")



	#下载文件
	def put(self, files, file_name):
		files.update_files()
		if file_name in files.files_list: #文件是否存在？

			req_protocol = Req_Protocol(CommandType.PUT, file_name, os.stat(file_name).st_size)
			req_header = req_protocol.make_packet_header()
			self.client_socket.sendall(req_header)

			print("正在传输上传文件...") #发送文件名和文件的大小

			#发送文件
			with open(file_name, 'rb') as file:
				while True:
					data = file.read(BUFSIZE)
					if not data:
						print("%s文件传输完成!"%file_name)
						break
					self.client_socket.send(data)

			res_header = self.client_socket.recv(RES_HEADER_SIZE)
			msgTyep, stateCode, file_size = struct.unpack(RES_HEADER_FORM, res_header)
			if stateCode == StateCode.OK:
				print("服务器接受成功！")
		else:
			print("不存在此文件！")



	#删除文件
	def delete(self, file_name):
		req_protocol = Req_Protocol(CommandType.DEL, file_name)
		req_header = req_protocol.make_packet_header()
		self.client_socket.sendall(req_header)

		print("正在删除%s..." % file_name)

		#ans表明服务器对是否存在对所要删除的文件是否存在的回答
		#res_header = self.client_socket.recv(RES_HEADER_SIZE)
		res_header = self.client_socket.recv(RES_HEADER_SIZE)
		msgTyep, stateCode, file_size = struct.unpack(RES_HEADER_FORM, res_header)

		if stateCode == StateCode.OK:
			print("删除成功！")
		else:
			print("服务器上不存在此文件！")


	def bye(self):
		req_protocol = Req_Protocol(CommandType.BYE)
		req_header = req_protocol.make_packet_header()
		self.client_socket.sendall(req_header)
		self.client_socket.close()
		







