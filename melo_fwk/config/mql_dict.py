
from melo_fwk.loggers.global_logger import GlobalLogger

class MqlDict(dict):

	def _strip(self, key: str, default=None):
		if default is not None:
			return self.get(key, default)
		assert key in self.keys(), \
			f"Key [{key}] not in Dictionary keys [{self.keys()}]"
		return self.get(key)

	def strip_single(self, key: str, default=None):
		val = self._strip(key)[0]
		return MqlDict(val) if isinstance(val, dict) else val

	def parse_list(self, key: str):
		str_list = self.strip_single(key)
		return [e.strip() for e in str_list.split(",")]

	def parse_num_list(self, key: str, default=None, type_=float):
		str_list = self.strip_single(key, default)
		return [type_(e.strip()) for e in str_list.split(",")]

