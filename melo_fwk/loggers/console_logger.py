from datetime import datetime

from melo_fwk.loggers.base_logger import BaseLogger


class ConsoleLogger(BaseLogger):
	def __init__(self, component: str):
		super(ConsoleLogger, self).__init__(component)

	def info(self, log_message: str):
		print(
			f"[{datetime.now()}] INFO ({self.component}): {log_message}"
		)

	def warn(self, log_message: str):
		print(
			f"[{datetime.now()}] WARN ({self.component}): {log_message}"
		)

	def error(self, log_message: str):
		print(
			f"[{datetime.now()}] ERROR({self.component}): {log_message}"
		)
