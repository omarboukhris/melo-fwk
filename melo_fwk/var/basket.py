from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

from melo_fwk.datastreams import TsarDataStream
from melo_fwk.market_data.product import Product

class VaRBasket:
	"""
	Should be able to find how to plot :
		returns hist
		var in hist
		generated price paths
		normal dist over returns hist
	"""

	def __init__(self, tsar_list: List[TsarDataStream], products: List[Product]):
		self.tsar_list = tsar_list
		self.dataframe = pd.DataFrame({
			product.name: product.get_close_series() for product in products
		}).ffill()
		self.tails = self.dataframe.tail(10).values.T
		self.S0 = self.dataframe.iloc[-1].to_numpy()
		self.pct_returns = self.dataframe.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
		self.mu = np.array(self.pct_returns.mean(axis=0))
		self.std = np.array(self.pct_returns.std(axis=0))

	def simulate_hist(self, n_days, sample_ratio: float, method: str = "gbm"):
		Z = np.sqrt(n_days) * self.pct_returns.sample(frac=sample_ratio, axis=0)
		if method == "gbm":
			drift = (self.mu - (self.std ** 2 / 2)) * n_days
			vol = np.einsum("i,ij->ij", np.sqrt(n_days) * self.std, Z.T)
			e = np.exp(vol + drift[:, np.newaxis])
			return np.nan_to_num(np.einsum("i,ij->ij", self.S0, e))
		else:  # method == "lin":
			e = 1+Z
			return np.nan_to_num(self.S0 * e).T

	def simulate_hist_paths(self, n_days, sample_ratio: float):
		S0 = self.S0
		P = []
		for _ in range(n_days):
			Z = self.pct_returns.sample(frac=sample_ratio, axis=0)
			e = 1+Z
			S0 = np.nan_to_num(S0 * e)
			P.append(S0.T)

		return np.einsum("i,ijk->jki", np.ones(1), np.array(P))

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

	def plot_hist(self, n_days, sample_ratio: float, method: str = "gbm"):
		price = self.simulate_hist(n_days, sample_ratio, method)
		for p in price:
			plt.hist(p, bins=int(len(p)/10))
			plt.show()
			plt.close()

	def plot_hist_paths(self, n_days, sample_ratio: float):
		price = self.simulate_hist_paths(n_days, sample_ratio)
		for t, p in zip(self.tails, price):
			plt.plot(np.concatenate((np.tile(t, (len(p), 1)).T, p.T)))
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

	def monte_carlo_VaR(self, alpha: float, n_days: int = 1, n_simulation: int = 100000, method: str = "single"):
		pose_vect = np.array([tsar.last_pose() for tsar in self.tsar_list])

		if method == "path":
			P = np.array(self.simulate_price_paths(n_days, n_simulation))[:, :, -1]
		else:  # single
			P = self.simulate_price(n_days, n_simulation)

		S = np.einsum("i,ij->ij", pose_vect, P)
		return [pd.Series(p).sort_values(ascending=True).quantile(alpha) for p in S]

	def histo_VaR(self, alpha: float, n_days: int = 1, sample_ratio: float = 0.6, method: str = "single"):
		pose_vect = np.array([tsar.last_pose() for tsar in self.tsar_list])

		if method == "path":
			P = np.array(self.simulate_hist_paths(n_days, sample_ratio))[:, :, -1]
		else:  # single
			P = self.simulate_hist(n_days, sample_ratio)

		S = np.einsum("i,ij->ij", pose_vect, P)
		return [pd.Series(p).sort_values(ascending=True).quantile(alpha) for p in S]

