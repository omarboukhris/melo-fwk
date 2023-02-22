

class EstimatorParameters:

	def __init__(self, estimator_params_dict):
		self.estimator_params = iter(estimator_params_dict)
		self.estimator_params_dict = estimator_params_dict

	def reset(self):
		self.estimator_params = iter(self.estimator_params_dict)

	def get(self, key: str):
		return self.estimator_params_dict.pop(key, None)

	def next_str_param(self, default_val):
		try:
			return next(self.estimator_params)
		except StopIteration:
			return default_val

	def next_int_param(self, default_val):
		return int(self.next_str_param(default_val))

	def next_float_param(self, default_val):
		return float(self.next_str_param(default_val))

