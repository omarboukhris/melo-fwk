
from core.rules.trade_rule import AbstractTradingRule
from core.datastreams import datastream as ds
from core.helpers import AccountPlotter

import pandas as pd
import numpy as np

class EWMATradingRule(AbstractTradingRule):

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

	def forcast(self, data: pd.DataFrame):
		"""
		data as pandas.dataframe :
			['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
		"""
		fast_ewma = data["Close"].ewm(span=self.hyper_params["fast_span"]).mean().to_numpy()
		slow_ewma = data["Close"].ewm(span=self.hyper_params["slow_span"]).mean().to_numpy()

		ewma = fast_ewma[-1] - slow_ewma[-1]
		forcast_value = self.hyper_params["scaling_factor"] * (ewma/slow_ewma.std())
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
	ewma = EWMATradingRule("sma", sma_params)

	output_forcast = []
	for _ in pds:
		window = pds.get_window()
		if window is not None:
			output_forcast.append({
				"Balance": ewma.forcast(window),
				"Date": pds.get_current_date(),
			})

	df = pd.DataFrame(output_forcast)
	print(df)
	# acc_plt = AccountPlotter(df)
	# acc_plt.plot()
