
import pandas as pd

class ITradingRule:

	def __init__(self, name: str, hyper_params: dict):
		self.name = name
		self.hyper_params = hyper_params

	def forecast(self, data: pd.DataFrame):
		"""
		data as pandas.dataframe :
			['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
		"""
		pass
