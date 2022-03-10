
from trade_rule import AbstractTradingRule
from core.datastreams import datastream as ds

import pandas as pd
import numpy as np

class SMATradingRule(AbstractTradingRule):

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

	def forcast(self, data: pd.DataFrame):
		"""
		data as pandas.dataframe :
			['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
		"""
		fast_ewma = np.array(data["Close"].ewm(span=self.hyper_params["fast_span"]).mean())
		slow_ewma = np.array(data["Close"].ewm(span=self.hyper_params["slow_span"]).mean())

		ewma = np.array(fast_ewma - slow_ewma)
		forcast_value = self.hyper_params["scaling_factor"] * (ewma.mean()/ewma.std())
		if forcast_value > 0:
			forcast_value = min(forcast_value, self.hyper_params["cap"])
		else:
			forcast_value = max(forcast_value, -self.hyper_params["cap"])

		return forcast_value


if __name__ == "__main__":

	df = pd.read_csv("../data/FB_1d_10y.csv")
	pds = ds.PandasDataStream(df)

	sma_params = {
		"fast_span": 4,
		"slow_span": 8,
		"scaling_factor": 20,
		"cap": 20,
	}
	sma = SMATradingRule("sma", sma_params)

	output_forcast = []
	for _ in pds:
		window = pds.get_window()
		if window is not None:
			output_forcast.append({
				"forcast": sma.forcast(window),
				"date": pds.get_current_date(),
			})

	print(output_forcast)
