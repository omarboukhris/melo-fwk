from datetime import datetime

from mutils.loggers.base_logger import BaseLogger


class StringStreamLogger(BaseLogger):
	def __init__(self, component: str):
		super(StringStreamLogger, self).__init__(component)
		self.ss = ""

	def info(self, log_message: str):
		self.ss += f"[{datetime.now()}] INFO ({self.component}): {log_message}"

	def warn(self, log_message: str):
		self.ss += f"WARN  [{datetime.now()}] ({self.component}): {log_message}"

	def error(self, log_message: str):
		self.ss += f"ERROR [{datetime.now()}] ({self.component}): {log_message}"
