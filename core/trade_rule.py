
import numpy as np
import pandas as pd

class AbstractTradingRule:

	def __init__(self, name: str):
		self.name = name

	def forcast(self, data: np.array):
		"""
		data as pandas.dataframe :
			['Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']
		"""
		pass


if __name__ == "__main__":
	pass
