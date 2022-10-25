from datetime import datetime

from melo_fwk.loggers.base_logger import BaseLogger


class ConsoleLogger(BaseLogger):
	def __init__(self, component: str):
		super(ConsoleLogger, self).__init__(component)

	def info(self, log_message: str):
		print(
			f"INFO  [{datetime.now()}] ({self.component}): {log_message}"
		)

	def warn(self, log_message: str):
		print(
			f"WARN  [{datetime.now()}] ({self.component}): {log_message}"
		)

	def error(self, log_message: str):
		print(
			f"ERROR [{datetime.now()}] ({self.component}): {log_message}"
		)
