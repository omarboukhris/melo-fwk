
import numpy as np
import pandas as pd

class AbstractTradingRule:

	def __init__(self, name: str):
		self.name = name

	def forcast(self, data: np.array):
		pass


if __name__ == "__main__":
	pass
