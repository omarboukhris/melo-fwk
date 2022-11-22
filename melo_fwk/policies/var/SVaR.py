from typing import Union

import numpy as np
import pandas as pd

from melo_fwk.policies.var.common import VaRFactory


class SVaR99:

	def __init__(self, n_days: int, sample_param: Union[float, int], method: str = "monte_carlo"):
		self.n_days = n_days
		self.sample_param = sample_param
		self.method = method
		self.alpha = 0.01

	def __call__(self, returns: pd.DataFrame, w: np.array, window_size: int = 250):
		_var = VaRFactory(self.method)(
			n_days=self.n_days,
			alpha=self.alpha
		)
		_var.set_sample_param(self.sample_param)

		var_list = []
		# rolling or expanding
		for returns_window in returns.rolling():
			var_list.append(_var(returns_window, w))

		# maybe return the whole list, or head
		return pd.DataFrame(var_list).head(10)
		# or return just min, will depend on reporting
		# return np.min(var_list)


