import socket
from protocol import *
import os
import threading
from protocol import *

BUFSIZE = 1024

class Client_For_Peer:
	def __init__(self, client_socket, server_ip, server_port):
		self.client_socket = client_socket
		self.server_ip = server_ip
		self.server_port = server_port


	#列取本地的文件OK
	def lsc(self, files):
		files.update_files()
		files_list = files.list_files()
		print("本地的所有文件如下：")
		for file in files_list:
			print("%s     %sbytes" % (file, os.stat(file).st_size))
		print("共%d个文件。"%len(files_list))

	#列取所有在线peer的所有文件及其大小
	def lsp(self):
		req_protocol = Req_Protocol(CommandType.LSP)
		req_header = req_protocol.make_packet_header()
		self.client_socket.sendall(req_header)

		res_header = self.client_socket.recv(RES_HEADER_SIZE)
		msgType, stateCode, size = struct.unpack(RES_HEADER_FORM, res_header)

		recvd_size = 0
		info = ''
		while recvd_size != size:
			if size - recvd_size > BUFSIZE:
				data = self.client_socket.recv(BUFSIZE)
				recvd_size += len(data)
			else:
				data = self.client_socket.recv(size - recvd_size)
				recvd_size += len(data)
			info += data.decode('utf-8')
		peers = info.split('//')
		while '' in peers:
			peers.remove('')
		for peer in peers:
			peer = peer.split(',')
			for i in range(len(peer)):
				if i == 0:
					if tuple([peer[i].split(' : ')[0], int(peer[i].split(' : ')[1])]) == self.client_socket.getsockname():
						break
					else:
						print('Peer[%s : %s]所有的文件：' % (peer[i].split(' : ')[0], peer[i].split(' : ')[1]))
				else:
					print('%s     %sbytes' % (peer[i].split(' : ')[0], peer[i].split(' : ')[1]))



	#询问服务器谁有指定的文件OK
	def who_have(self, file_name):##是ask命令！
		req_protocol = Req_Protocol(CommandType.ASK, file_name)
		req_header = req_protocol.make_packet_header()
		self.client_socket.sendall(req_header)

		res_header = self.client_socket.recv(RES_HEADER_SIZE)
		msgType, stateCode, size = struct.unpack(RES_HEADER_FORM, res_header)

		recvd_size = 0
		peers_info = ''
		while recvd_size != size:
			if size - recvd_size > BUFSIZE:
				data = self.client_socket.recv(BUFSIZE)
				recvd_size += len(data)
			else:
				data = self.client_socket.recv(size - recvd_size)
				recvd_size += len(data)
			peers_info += data.decode('utf-8')

		peers = peers_info.split('//')
		while '' in peers:
			peers.remove('')
		file_size = peers[0]
		file_size = int(file_size)
		peers.pop(0)
		peers_have_files = []
		for peer in peers:
			peer_ip = peer.split(' : ')[0]
			peer_port = peer.split(' : ')[1]
			if (peer_ip, int(peer_port)) != self.client_socket.getsockname():
				peers_have_files.append((peer_ip, int(peer_port)))
		return (peers_have_files,  file_size)


	#从拥有所需文件的peer处下载文件
	def get(self, files, file_name):
		print('正在下载%s文件...'%file_name)
		files.update_files()
		peers_have_files, file_size = self.who_have(file_name)
		num_peers_have_files = len(peers_have_files)

		if num_peers_have_files:
			each_peer_provide = file_size // num_peers_have_files
			remain = file_size % num_peers_have_files

			temp_dir = []
			threads = []
			for i in range(0, num_peers_have_files-1):
				temp_dir.append(file_name+str(i))
				deal = threading.Thread(target = self.connect_to_peer, 
					args = (file_name, each_peer_provide, 0, i, peers_have_files[i]))
				threads.append(deal)
			i = num_peers_have_files - 1
			deal = threading.Thread(target = self.connect_to_peer, 
					args = (file_name, each_peer_provide, remain, i, peers_have_files[i]))
			threads.append(deal)
			temp_dir.append(file_name+str(i))

			for deal in threads:
				deal.start()

			for deal in threads:
				deal.join()

			#如何判断线程都执行完了？
			files.update_files()
			print("原文件名：" + file_name)
			while file_name in files.files_list:
					file_name = 'new_' + file_name
			print("下载后文件名：" + file_name)
			with open(file_name, 'wb') as newfile:
				for part_file in temp_dir:
					with open(part_file, 'rb') as part:
						data = part.read()
					newfile.write(data)
					os.remove(part_file)
			files.update_files()
			temp_dir.clear()
			print("文件下载成功！")
		else:
			print("没有任何一个peer具有该文件！")


		
	#与peer直接建立连接
	def connect_to_peer(self, file_name, file_size, remain, index, peer_addr):
		print('正在从[%s : %s]'%(peer_addr) + '处下载文件%s'%file_name)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect(peer_addr)
		start_from = index * file_size
		file_size = file_size + remain

		req_protocol = Req_Protocol(CommandType.GET, file_name, struct.calcsize('ll'))
		req_header = req_protocol.make_packet_header()
		sock.sendall(req_header)
		sock.sendall(struct.pack('ll', start_from, file_size))

		res_header = sock.recv(RES_HEADER_SIZE)
		msgType, stateCode, size = struct.unpack(RES_HEADER_FORM, res_header)

		recv_size = 0
		file_name += str(index)
		with open(file_name, 'wb') as newfile:
			while recv_size != file_size:
				if file_size - recv_size > BUFSIZE:
					data = sock.recv(BUFSIZE)
					recv_size += len(data)
				else:
					data = sock.recv(file_size - recv_size)
					recv_size += len(data)
				newfile.write(data)
		sock.close()
		



	#询问哪个peer有相关文件OK
	def ask(self, file_name):
		peers_have_files, file_size = self.who_have(file_name)
		if len(peers_have_files):
			print("以下peer拥有所询问的文件：")
			print("文件的大小为%sbytes" % file_size)
			for peer in peers_have_files:
				print("[%s : %s]" % (peer))



	#列取所有peer的ip和端口信息Ok
	def peer(self):
		req_protocol = Req_Protocol(CommandType.PEER)
		req_header = req_protocol.make_packet_header()
		self.client_socket.sendall(req_header)

		res_header = self.client_socket.recv(RES_HEADER_SIZE)
		msgType, stateCode, size = struct.unpack(RES_HEADER_FORM, res_header)
		print('所有在线peer：')

		recvd_size = 0
		peers_info = ''
		while recvd_size != size:
			if size - recvd_size > BUFSIZE:
				data = self.client_socket.recv(BUFSIZE)
				recvd_size += len(data)
			else:
				data = self.client_socket.recv(size - recvd_size)
				recvd_size += len(data)
			peers_info += data.decode('utf-8')
		
		peers = peers_info.split('//')
		index = 0
		while '' in peers:
			peers.remove('')
		for peer in peers:
			print('%d [%s]'%(index, peer))
			index += 1
		
	def bye(self):
		req_protocol = Req_Protocol(CommandType.BYE)
		req_header = req_protocol.make_packet_header()
		self.client_socket.sendall(req_header)
		self.client_socket.close()





class Server_For_Peer:
	def __init__(self, server_socket):
		self.server_socket = server_socket
		self.server_ip, self.server_port = server_socket.getsockname()

	#处理其他peer的连接，响应其他peer获取某些文件的需求
	def deal_get(self, files, file_name):
		data = self.server_socket.recv(struct.calcsize('ll'))
		start_from, file_size = struct.unpack('ll', data)
		res_protocol = Res_Protocol(StateCode.OK, file_size)
		res_header = res_protocol.make_packet_header()
		self.server_socket.sendall(res_header)
		with open(file_name, 'rb') as file:
			file.seek(start_from)
			while file_size:
				if file_size > BUFSIZE:
					data = file.read(BUFSIZE)
					file_size -= BUFSIZE
				else:
					data = file.read(file_size)
					file_size = 0
				self.server_socket.send(data)
		

	#处理服务器获取全部文件信息的请求
	def deal_lsp(self, files):
		my_info = '%s : %s' % (self.server_ip, self.server_port)
		files.update_files()
		files_list = files.list_files()
		for file in files_list:
			my_info += ',' + file + ' : ' + str(os.stat(file).st_size)
		my_info = my_info.encode('utf-8')
		res_protocol = Res_Protocol(StateCode.OK, len(my_info))
		res_header = res_protocol.make_packet_header()
		self.server_socket.sendall(res_header)
		self.server_socket.sendall(my_info)

	#回答服务器是否拥有某个文件
	def deal_ask(self, files, file_name):
		files.update_files()
		files_list = files.list_files()
		if file_name in files_list:
			res_protocol = Res_Protocol(StateCode.OK, os.stat(file_name).st_size)
			res_header = res_protocol.make_packet_header()
			self.server_socket.sendall(res_header)
		else:
			res_protocol = Res_Protocol(StateCode.NOTFOUND)
			res_header = res_protocol.make_packet_header()
			self.server_socket.sendall(res_header)



		

