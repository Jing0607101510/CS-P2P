import struct

REQ_HEADER_SIZE = struct.calcsize('ll128sl')
REQ_HEADER_FORM = 'll128sl'

RES_HEADER_SIZE = struct.calcsize('lll')
RES_HEADER_FORM = 'lll'


class MessageType:
	REQ = 0
	RES = 1

class CommandType:
	LSS = 0
	PUT = 1
	GET = 2
	DEL = 3
	BYE = 4
	LSP = 5
	ASK = 6
	PEER = 7

class StateCode:
	OK = 200
	NOTFOUND = 404
	FAIL = 500
	READY = 600


class Req_Protocol:
	def __init__(self, cmdType, sourseName = '', size = 0):
		self.msgType =  MessageType.REQ
		self.cmdType = cmdType
		self.sourseName = sourseName
		self.size = size

	def make_packet_header(self):
		header = struct.pack('ll128sl', self.msgType, self.cmdType, 
				self.sourseName.encode('utf-8'), self.size)
		return header

class Res_Protocol:
	def __init__(self, stateCode, size = 0):
		self.msgType = MessageType.RES
		self.stateCode = stateCode
		self.size = size

	def make_packet_header(self):
		header  = struct.pack('lll', self.msgType, self.stateCode, self.size)
		return header

