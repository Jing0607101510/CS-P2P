from socket import *
from time import ctime
import threading
import os
import struct
import sys
from protocol import *

BUFSIZE = 1024

class Server:
	def __init__(self, server_socket):
		self.server_socket = server_socket
		self.server_ip, self.server_port = server_socket.getsockname()
		self.connect_list_addr = []

	#处理peer的列取其他peer的所有文件及大小的请求
	def deal_lsp(self, server):
		peers_files = []
		tasks = []
		for peer in server.connect_list_addr:
			deal  = threading.Thread(target = self.connect_to_peer, 
				args = (peers_files, peer))
			tasks.append(deal)

		for deal in tasks:
			deal.start()
		for deal in tasks:
			deal.join()
		return_info = ''
		for info in peers_files:
			return_info += info+'//'

		return_info = return_info.encode('utf-8')
		res_protocol = Res_Protocol(StateCode.OK, len(return_info))
		res_header = res_protocol.make_packet_header()
		self.server_socket.sendall(res_header)

		self.server_socket.sendall(return_info)
		print("请求成功")


	#服务器连接至远程的peer
	def connect_to_peer(self, peers_files, peer_addr):
		sock = socket(AF_INET, SOCK_STREAM)
		try:
			sock.connect(peer_addr)

			req_protocol = Req_Protocol(CommandType.LSP)
			req_header = req_protocol.make_packet_header()
			sock.sendall(req_header)

			res_header = sock.recv(RES_HEADER_SIZE)
			msgType, stateCode, size = struct.unpack(RES_HEADER_FORM, res_header)

			recvd_size = 0
			info = ''
			while recvd_size != size:
				if size - recvd_size > BUFSIZE:
					data = sock.recv(BUFSIZE)
					recvd_size += len(data)
				else:
					data = sock.recv(size - recvd_size)
					recvd_size += len(data)
				info += data.decode('utf-8')

			peers_files.append(info)
			sock.close()
		except Exception as msg:
			print(msg)
			sock.close()
			print('发生错误!')


	#处理peer询问谁有指定文件的请求
	def deal_ask(self, server, file_name):
		peer_info = ['0']
		tasks = []
		file_size = 0
		for peer in server.connect_list_addr:
			deal = threading.Thread(target = self.ask_file, args = (peer_info, file_name, peer))
			tasks.append(deal)
		for deal in tasks:
			deal.start()
		for deal in tasks:
			deal.join()
		info = ''
		for i in peer_info:
			info += i + '//'
		info = info.encode('utf-8')
		res_protocol = Res_Protocol(StateCode.OK, len(info))
		res_header = res_protocol.make_packet_header()
		self.server_socket.sendall(res_header)
		self.server_socket.sendall(info)
		print("请求成功")
		

	#向每一个peer询问是否拥有某个文件
	def ask_file(self, peer_info, file_name, peer_addr):
		sock = socket(AF_INET, SOCK_STREAM)
		try:
			sock.connect(peer_addr)

			req_protocol = Req_Protocol(CommandType.ASK, file_name)
			req_header = req_protocol.make_packet_header()
			sock.sendall(req_header)

			res_header = sock.recv(RES_HEADER_SIZE)
			msgType, stateCode, size = struct.unpack(RES_HEADER_FORM, res_header)
			
			if stateCode == StateCode.OK:
				peer_info.append('%s : %s'%peer_addr)
				peer_info[0] = str(size)
			sock.close()
		except Exception as msg:
			print(msg)
			sock.close()
			print('发生错误!')

	#处理peer获取当前在线peer的信息
	def deal_peer(self, server):
		peer_info = ''
		for peer in server.connect_list_addr:
			if peer != self.server_socket.getpeername():
				peer_info += '%s : %s//'%(peer)
		peer_info = peer_info.encode('utf-8')

		res_protocol = Res_Protocol(StateCode.OK, len(peer_info))
		res_header = res_protocol.make_packet_header()
		self.server_socket.sendall(res_header)

		self.server_socket.sendall(peer_info)

		print("请求成功")

