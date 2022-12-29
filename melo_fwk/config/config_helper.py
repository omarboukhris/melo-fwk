
from melo_fwk.loggers.global_logger import GlobalLogger

class ConfigBuilderHelper:

	@staticmethod
	def strip(parsed_dict: dict, key: str):
		assert key in parsed_dict.keys(), \
			f"Key [{key}] not in Dictionary keys [{parsed_dict.keys()}]"
		return parsed_dict[key]

	@staticmethod
	def strip_single(parsed_dict: dict, key: str):
		return ConfigBuilderHelper.strip(parsed_dict, key)[0]

	@staticmethod
	def parse_list(parsed_dict: dict, key: str):
		str_list = ConfigBuilderHelper.strip_single(parsed_dict, key)
		return [e.strip() for e in str_list.split(",")]

	@staticmethod
	def parse_num_list(parsed_dict: dict, key: str):
		str_list = ConfigBuilderHelper.strip_single(parsed_dict, key)
		return [float(e.strip()) for e in str_list.split(",")]

