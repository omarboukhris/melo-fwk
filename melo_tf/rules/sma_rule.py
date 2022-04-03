
from melo_tf.rules.trade_rule import ITradingRule
from melo_tf.datastreams import datastream as ds
from melo_tf.helpers import AccountPlotter

import pandas as pd
import numpy as np
import math

class SMATradingRule(ITradingRule):

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
		fast_sma = data["Close"].rolling(self.hyper_params["fast_span"]).mean()
		slow_sma = data["Close"].rolling(self.hyper_params["slow_span"]).mean()

		sma = fast_sma.iloc[-1] - slow_sma.iloc[-1]
		forecast_value = self.hyper_params["scaling_factor"] * (sma / slow_sma.std())
		if forecast_value > 0:
			forecast_value = min(forecast_value, self.hyper_params["cap"])
		else:
			forecast_value = max(forecast_value, -self.hyper_params["cap"])

		return forecast_value


if __name__ == "__main__":

	df = pd.read_csv("../data/FB_1d_10y.csv")
	pds = ds.PandasDataStream(df)

	sma_params = {
		"fast_span": 4,
		"slow_span": 8,
		"scaling_factor": 20,
		"cap": 20,
	}
	sma_rule = SMATradingRule("sma", sma_params)

	output_forcast = []
	for _ in pds:
		window = pds.get_window()
		if window is not None:
			output_forcast.append({
				"Balance": sma_rule.forecast(window),
				"Date": pds.get_current_date(),
			})

	df = pd.DataFrame(output_forcast)
	print(df)
	# acc_plt = AccountPlotter(df)
	# acc_plt.plot()
