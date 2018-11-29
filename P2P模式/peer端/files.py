import os
class Files:
	def __init__(self, path):
		self.path = path
		self.files_list = []
		self.files_num = 0;
		self.update_files()

	#更新文件列表
	def update_files(self):
		self.files_list.clear()
		self.files_num = 0
		dirs = os.listdir(self.path)
		for file in dirs:
			if os.path.isfile(file):
				self.files_num += 1
				self.files_list.append(file)


	#获取文件列表
	def list_files(self):
		return self.files_list[:]


