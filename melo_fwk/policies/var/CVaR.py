from typing import Union

import numpy as np
import pandas as pd

from melo_fwk.policies.var.common import VaRFactory


class CVaR97:

	def __init__(self, n_days: int, sample_param: Union[float, int], method: str = "monte_carlo"):
		self.n_days = n_days
		self.sample_param = sample_param
		self.method = method
		self.alpha = 0.025

	def __call__(self, returns: pd.DataFrame, w: np.array, nbins: int = 1e+2):
		var_list = []
		step_size = self.alpha / nbins
		alpha = step_size

		var_class_ = VaRFactory(self.method)
		for i in range(nbins):
			_var = var_class_(
				n_days=self.n_days,
				alpha=alpha
			)
			_var.set_sample_param(self.sample_param)
			var_list.append(_var(returns, w))
			alpha += step_size

		return np.mean(var_list)
