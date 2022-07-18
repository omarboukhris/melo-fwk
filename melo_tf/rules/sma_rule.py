
import rules.trade_rule as tr

import pandas as pd

class SMATradingRule(tr.ITradingRule):

	def __init__(self, name: str, hyper_params: dict):
		"""
		:param name: Strategy's name
		:param hyper_params: dict with parameters :
			fast_span
			slow_span
			scaling_factor
			cap
		"""
		super(SMATradingRule, self).__init__(name, hyper_params)

	def forecast(self, data: pd.DataFrame):
		"""
		data as pandas.dataframe :
			['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
		"""
		fast_sma = data["Close"].rolling(int(self.hyper_params["fast_span"])).mean()
		slow_sma = data["Close"].rolling(int(self.hyper_params["slow_span"])).mean()

		sma = fast_sma.iloc[-1] - slow_sma.iloc[-1]
		# sma = fast_sma.mean() - slow_sma.mean()  # this is whole thing needs to be fire proofed

		# forecast_value = self.hyper_params["scale"] * (sma / slow_sma.std())
		forecast_value = sma
		if forecast_value > 0:
			forecast_value = min(forecast_value, self.hyper_params["cap"])
		else:
			forecast_value = max(forecast_value, -self.hyper_params["cap"])

		return forecast_value
