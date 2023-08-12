
class MqlDict(dict):

	def _get_node(self, key: str, default=None):
		if key not in self.keys():
			print(f"Warning {MqlDict.__name__}: Key [{key}] not in Dictionary keys [{self.keys()}]")
		return self.get(key, default)

	def get_node(self, key: str, default=None):
		val = self._get_node(key, default)[0]
		return MqlDict(val) if isinstance(val, dict) else val

	def parse_list(self, key: str, sep=","):
		str_list = self.get_node(key)
		return [e.strip() for e in str_list.split(sep)]

	def parse_num_list(self, key: str, default=None, type_=float, sep=","):
		str_list = self.get_node(key, default)
		return [type_(e.strip()) for e in str_list.split(sep)]
