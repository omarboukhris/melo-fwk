
from dataclasses import dataclass

import pandas as pd
import numpy as np

@dataclass(frozen=True)
class SMATradingRule:
	fast_span: int
	slow_span: int
	scale: float
	cap: float

	search_space = {
		"fast_span": [i for i in range(4, 60)],
		"slow_span": [i for i in range(8, 100)],
		"scale": [1.],
		"cap": [20]
	}

	def forecast_vect(self, data: pd.DataFrame):
		"""
		data as pandas.dataframe :
			['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
		"""
		fast_sma = data["Close"].rolling(int(self.fast_span)).mean()
		slow_sma = data["Close"].rolling(int(self.slow_span)).mean()

		std = data["Close"].rolling(25).std()

		sma = fast_sma - slow_sma

		np.seterr(invalid="ignore")
		forecast_vect = self.scale * (sma / std)
		np.seterr(invalid="warn")
		return forecast_vect.fillna(0)

	def forecast_vect_cap(self, data: pd.DataFrame):
		f_vect = self.forecast_vect(data)
		f_series = pd.Series([
			min(f_val, self.cap) if f_val > 0 else max(f_val, -self.cap)
			for f_val in f_vect
		])
		return f_series

	def forecast(self, data: pd.DataFrame):
		cap_f_vect = self.forecast_vect_cap(data)
		assert len(cap_f_vect) > 0, "(SMATradingRule) empty forecast vector"
		return cap_f_vect.iat[-1]
