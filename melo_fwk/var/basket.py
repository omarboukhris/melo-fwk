from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

from melo_fwk.market_data.product import Product

class VaRBasket:
	"""
	Should be able to find how to plot :
		returns hist
		var in hist
		generated price paths
		normal dist over returns hist
	"""

	def __init__(self, returns: List[Product], weights: List[float]):
		assert len(returns) == len(weights), \
			f"Returns and weights don't correspond : len {len(returns)} == {len(weights)}"
		self.dataframe = pd.DataFrame({
			ret.name: ret.get_close_series() for ret in returns
		}).ffill()
		self.tails = self.dataframe.tail(10).values.T
		self.w = np.array(weights)
		self.w_returns = self.w * self.dataframe
		self.S0 = self.dataframe.iloc[-1].to_numpy()
		self.pct_returns = self.dataframe.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
		self.mu = np.array(self.pct_returns.mean(axis=0))
		self.std = np.array(self.pct_returns.std(axis=0))

	def simulate_hist(self, n_days, sample_ratio: float):
		Z = np.sqrt(n_days) * self.pct_returns.sample(frac=sample_ratio, axis=0)
		e = 1+Z
		return np.nan_to_num(self.S0 * e).T

	def get_cholesky(self):
		corr_mat = self.pct_returns.corr()
		return corr_mat, np.linalg.cholesky(corr_mat.to_numpy())

	def simulate_price(self, n_days: int = 1, n_simulation: int = 100000):
		corr_mat, L = self.get_cholesky()
		Z = np.matmul(L, norm.rvs(size=[len(corr_mat.columns), n_simulation]))
		drift = (self.mu - (self.std ** 2 / 2)) * n_days
		vol = np.einsum("i,ij->ij", np.sqrt(n_days) * self.std, Z)
		e = np.exp(vol + drift[:, np.newaxis])

		return np.nan_to_num(np.einsum("i,ij->ij", self.S0, e))

	def plot_hist(self, n_days, sample_ratio: float):
		price = self.simulate_hist(n_days, sample_ratio)
		for p in price:
			plt.hist(p, bins=int(len(p)/10))
			plt.show()
			plt.close()

	def plot_price(self, n_days: int = 1, n_simulation: int = 100000):
		price = self.simulate_price(n_days, n_simulation)
		for p in price:
			plt.hist(p, bins=int(len(p)/10))
			plt.show()
			plt.close()

	def plot_price_paths(self, n_days: int = 1, n_simulation: int = 100000):
		price = self.simulate_price_paths(n_days, n_simulation)
		for t, p in zip(self.tails, price):
			plt.plot(np.concatenate((np.tile(t, (len(p), 1)).T, p.T)))
			plt.show()
			plt.close()

	def simulate_price_paths(self, n_days: int = 1, n_simulation: int = 100000):
		corr_mat, L = self.get_cholesky()
		drift = self.mu - (self.std ** 2 / 2)
		Z = np.array([
			drift + self.std * np.matmul(
				L, norm.rvs(size=[len(corr_mat.columns), n_simulation])).T
			for _ in range(n_days)
		]).T
		e = np.exp(np.cumsum(Z, 2))

		return np.nan_to_num(np.einsum("i,ijk->ijk", self.S0, e))

