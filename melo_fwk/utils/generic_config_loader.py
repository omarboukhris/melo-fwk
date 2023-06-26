import json
from typing import List, Union


class GenericConfigLoader:
	global_config = None

	def __init__(self, config: Union[str, List[str]]):
		self.config_map = {}
		if isinstance(config, str):
			self.load_config(config)
		else:  # List[str]
			for c in config:
				self.load_config(c)

	@staticmethod
	def setup(config: Union[str, List[str]]):
		GenericConfigLoader.global_config = GenericConfigLoader(config)

	@staticmethod
	def get_node(key: str, default: object = None):
		return GenericConfigLoader.global_config.get(key, default)

	def load_config(self, c: str):
		try:
			with open(c, "r") as fs:
				self.config_map.update(json.load(fs))
		except FileNotFoundError as e:
			print(e)
			exit()

	def get(self, key: str, default: object = None):
		default = {} if default is None else default
		config_node = self.config_map.get(key, default)
		if GenericConfigLoader.is_sym_node(config_node):
			return {self.config_map[c] for c in config_node}
		elif isinstance(config_node, str):
			return self.config_map[config_node[1:]] if config_node and config_node[0] == "$" else config_node
		return config_node

	@staticmethod
	def is_sym_node(node) -> bool:
		return isinstance(node, list) and len(node) > 0 and isinstance(node[0], list)
