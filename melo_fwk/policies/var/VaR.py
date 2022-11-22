from typing import Union

import numpy as np
import pandas as pd

from melo_fwk.policies.var.common import VaRFactory


class VaR99:

	def __init__(self, n_days: int, sample_param, method: str = "monte_carlo"):
		self._var = VaRFactory(method)(
			alpha=0.01,
			n_days=n_days
		)
		self._var.set_sample_param(sample_param)

	def __call__(self, returns: pd.DataFrame, w: np.array):
		return self._var(returns, w)

class VaR95:

	def __init__(self, n_days: int, sample_param, method: str = "monte_carlo"):
		self._var = VaRFactory(method)(
			alpha=0.05,
			n_days=n_days
		)
		self._var.set_sample_param(sample_param)

	def __call__(self, returns: pd.DataFrame, w: np.array):
		return self._var(returns, w)
