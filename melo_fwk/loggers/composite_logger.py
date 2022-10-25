
from melo_fwk.loggers.base_logger import BaseLogger

from typing import List

class CompositeLogger(BaseLogger):

	def __init__(self, loggers: List[BaseLogger]):
		super(CompositeLogger, self).__init__("")
		self.loggers = loggers

	def info(self, log_message: str):
		for logger in self.loggers:
			logger.info(log_message)

	def warn(self, log_message: str):
		for logger in self.loggers:
			logger.warn(log_message)

	def error(self, log_message: str):
		for logger in self.loggers:
			logger.error(log_message)