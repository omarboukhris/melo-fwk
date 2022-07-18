
import rules.trade_rule as tr

import pandas as pd
import numpy as np

class EWMATradingRule(tr.ITradingRule):

	def __init__(self, name: str, hyper_params: dict):
		"""
		:param name: Strategy's name
		:param hyper_params: dict with parameters :
			fast_span
			slow_span
			scaling_factor
			cap
		"""
		super(EWMATradingRule, self).__init__(name, hyper_params)

	def forecast(self, data: pd.DataFrame):
		"""
		data as pandas.dataframe :
			['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
		"""
		fast_ewma = data["Close"].ewm(span=int(self.hyper_params["fast_span"])).mean().to_numpy()
		slow_ewma = data["Close"].ewm(span=int(self.hyper_params["slow_span"])).mean().to_numpy()

		std = data["Close"].ewm(span=int(self.hyper_params["fast_span"])).std().to_numpy()

		ewma = fast_ewma - slow_ewma

		np.seterr(invalid="ignore")
		forecast_vect = self.hyper_params["scale"] * (ewma / std)
		np.seterr(invalid="warn")

		forecast_value = forecast_vect[-1]
		if forecast_value > 0:
			forecast_value = min(forecast_value, self.hyper_params["cap"])
		else:
			forecast_value = max(forecast_value, -self.hyper_params["cap"])

		return forecast_value
