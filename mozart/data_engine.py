from mozart.shared_memory_map import SharedMemoryMap


class DataEngine:

	def __init__(self, shared_memory_map: SharedMemoryMap, process_nodes: list):
		self.shared_memory_map = shared_memory_map
		self.process_nodes = process_nodes

	def run(self, use_thread: bool = False):
		if use_thread:
			self.run_thread_pool()
		else:
			self.run_sequence()

	def run_thread_pool(self):
		pass

	def run_sequence(self):
		for node_class in self.process_nodes:
			node_instance = node_class()
			params = self.shared_memory_map.get_dependency(node_class)
			node_result = node_instance.run(*params)
			self.shared_memory_map.update(node_result)
