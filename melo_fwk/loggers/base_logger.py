
class BaseLogger:
	def __init__(self, component: str):
		self.component = component
		self.ss = ""

	def info(self, log_message: str):
		pass

	def warn(self, log_message: str):
		pass

	def error(self, log_message: str):
		pass

	def err(self, log_message: str):
		self.error(log_message)
