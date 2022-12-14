from typing import List

import numpy as np
from matplotlib import pyplot as plt

class VarPlotter:

	@staticmethod
	def save_prices(prices: np.array, export_filename: List[str]):
		for p, fn in zip(prices, export_filename):
			plt.hist(p, bins=int(len(p)/10))
			plt.savefig(fn)
			plt.close()

	@staticmethod
	def save_price_paths(prices: np.array, tails: np.array, export_filename: List[str]):
		for t, p, fn in zip(tails, prices, export_filename):
			plt.plot(np.concatenate((np.tile(t, (len(p), 1)).T, p.T)))
			plt.savefig(fn)
			plt.close()

	@staticmethod
	def plot_prices(prices: np.array):
		for p in prices:
			plt.hist(p, bins=int(len(p)/10))
			plt.show()
			plt.close()

	@staticmethod
	def plot_price_paths(prices: np.array, tails: np.array):
		for t, p in zip(tails, prices):
			plt.plot(np.concatenate((np.tile(t, (len(p), 1)).T, p.T)))
			plt.show()
			plt.close()
