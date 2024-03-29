from typing import Union

import numpy as np
import pandas as pd
from tqdm import tqdm

class SVaR99:

	def __init__(self, n_days: int, sample_param, method: str = "monte_carlo", model: str = "gbm"):
		self.n_days = n_days
		self.sample_param = sample_param
		self.method = method
		self.model = model
		self.alpha = 0.01

	def __call__(self, returns: pd.DataFrame, window_size: int = 250):
		_var = 0

		var_list = []
		# rolling or expanding
		indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=window_size)
		for returns_window in tqdm(returns.rolling(indexer, min_periods=window_size, step=25)):
			if len(returns_window) != window_size:
				break
			var_list.append(_var)

		# maybe return the whole list, or head
		# return pd.Series(var_list).sort_values(ascending=True).head(10)
		return pd.Series(var_list).min()
		# or return just min, will depend on reporting
		# return np.min(var_list)


