

class EstimatorParameters:

	def __init__(self, estimator_params_dict: dict):
		self.estimator_params_dict = estimator_params_dict

	def get(self, key: str, default: object = None):
		return self.estimator_params_dict.get(key, default)
