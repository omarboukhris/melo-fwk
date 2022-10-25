
from melo_fwk.loggers.composite_logger import CompositeLogger

from typing import List

class GlobalLogger:
	loggers: List[callable] = []

	@staticmethod
	def build_composite_for(component: str):
		return CompositeLogger([logger_class_(component) for logger_class_ in GlobalLogger.loggers])

	@staticmethod
	def set_loggers(loggers: List[callable]):
		GlobalLogger.loggers = loggers
