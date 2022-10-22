
from melo_fwk.strategies.base_strat import BaseStrategy

from dataclasses import dataclass

import pandas as pd
import numpy as np



@dataclass
class EWMAParamSpace:
	fast_span: int
	slow_span: int

	search_space = {
		"fast_span": [i for i in range(4, 60)],
		"slow_span": [i for i in range(8, 100)],
	}

@dataclass
class EWMAStrategy(BaseStrategy, EWMAParamSpace):

	def forecast_vect(self, data: pd.Series):
		"""
		data as pandas.dataframe :
			['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
		"""
		fast_ewma = data.ewm(span=int(self.fast_span)).mean()
		slow_ewma = data.ewm(span=int(self.slow_span)).mean()
		std = data.ewm(span=36).std()

		ewma = fast_ewma - slow_ewma

		np.seterr(invalid="ignore")
		forecast_vect = self.scale * (ewma / std)
		np.seterr(invalid="warn")
		return forecast_vect

	def forecast_vect_cap(self, data: pd.Series):
		f_vect = self.forecast_vect(data)
		f_series = pd.Series([
			min(f_val, self.cap) if f_val > 0 else max(f_val, -self.cap)
			for f_val in f_vect
		])
		return f_series

	def forecast(self, data: pd.Series):
		cap_f_vect = self.forecast_vect_cap(data)
		assert len(cap_f_vect) > 0, "(EWMAStrategy) empty forecast vector"
		return cap_f_vect.iat[-1]
