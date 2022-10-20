
from dataclasses import dataclass

import pandas as pd
import numpy as np


@dataclass(frozen=True)
class EWMATradingRule:
	fast_span: int = 0
	slow_span: int = 0
	scale: float = 0
	cap: float = 0

	search_space = {
		"fast_span": [i for i in range(4, 60)],
		"slow_span": [i for i in range(8, 100)],
		"scale": [1.],
		"cap": [20]
	}

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
		assert len(cap_f_vect) > 0, "(EWMATradingRule) empty forecast vector"
		return cap_f_vect.iat[-1]
