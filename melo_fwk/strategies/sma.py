
from melo_fwk.strategies.base_strat import BaseStrategy

from dataclasses import dataclass

import pandas as pd
import numpy as np

@dataclass
class SMAParamSpace:
	fast_span: int
	slow_span: int

	search_space = {
		"fast_span": [i for i in range(4, 60)],
		"slow_span": [i for i in range(8, 100)],
	}

@dataclass
class SMAStrategy(BaseStrategy, SMAParamSpace):

	def forecast_vect(self, data: pd.Series):
		fast_sma = data.rolling(int(self.fast_span)).mean()
		slow_sma = data.rolling(int(self.slow_span)).mean()

		std = data.rolling(25).std()

		sma = fast_sma - slow_sma

		np.seterr(invalid="ignore")
		forecast_vect = self.scale * (sma / std)
		np.seterr(invalid="warn")
		return forecast_vect

	def forecast_vect_cap(self, data: pd.Series):
		f_vect = self.forecast_vect(data)
		f_series = pd.Series([
			min(f_val, self.cap) if f_val > 0 else max(f_val, -self.cap)
			for f_val in f_vect
		])
		return f_series

