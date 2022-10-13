
from dataclasses import dataclass

import pandas as pd
import numpy as np

@dataclass(frozen=True)
class SMATradingRule:
	fast_span: int
	slow_span: int
	scale: float
	cap: float

	def forecast(self, data: pd.DataFrame):
		"""
		data as pandas.dataframe :
			['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
		"""
		fast_sma = data["Close"].rolling(int(self.fast_span)).mean().to_numpy()
		slow_sma = data["Close"].rolling(int(self.slow_span)).mean().mean()

		std = data["Close"].rolling(25).mean().std()

		sma = fast_sma - slow_sma

		np.seterr(invalid="ignore")
		forecast_vect = self.scale * (sma / std)
		np.seterr(invalid="warn")

		forecast_value = forecast_vect[-1]
		if forecast_value > 0:
			forecast_value = min(forecast_value, self.cap)
		else:
			forecast_value = max(forecast_value, -self.cap)

		return forecast_value
