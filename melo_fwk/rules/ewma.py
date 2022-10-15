
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
		"scale": [6.5],
		"cap": [20]
	}

	def forecast(self, data: pd.DataFrame):
		"""
		data as pandas.dataframe :
			['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
		"""
		fast_ewma = data["Close"].ewm(span=int(self.fast_span)).mean().to_numpy()
		slow_ewma = data["Close"].ewm(span=int(self.slow_span)).mean().to_numpy()

		std = data["Close"].ewm(span=36).std().to_numpy()

		ewma = fast_ewma - slow_ewma

		np.seterr(invalid="ignore")
		forecast_vect = self.scale * (ewma / std)
		np.seterr(invalid="warn")

		forecast_value = forecast_vect[-1]
		if forecast_value > 0:
			forecast_value = min(forecast_value, self.cap)
		else:
			forecast_value = max(forecast_value, -self.cap)

		return forecast_value
