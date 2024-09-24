from inspect import signature


class SharedMemoryMap(dict):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def get_dependency(self, node_class):
		try:
			data_dependency = node_class.data_dependency
		except AttributeError:
			data_dependency = signature(node_class.run)
		except Exception as e:
			raise e
		missing = [x for x in data_dependency if x in self.keys()]
		if len(missing) != 0:
			raise AssertionError(f"Missing parameters in shared memory map: {missing}")
		data_map = dict(map(lambda x: (x, self.get(x)), data_dependency))
		return data_map
