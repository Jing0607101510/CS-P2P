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


	#删除文件
	def del_files(self, file_name):
		if file_name in self.files_list:
			try:
				os.remove(file_name)
			except:
				print("删除失败！")
			else:
				self.update_files()
				print("删除成功！")
		else:
			print("不存在此文件")
