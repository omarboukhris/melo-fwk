from typing import List

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

from melo_fwk.datastreams import TsarDataStream
from melo_fwk.market_data.product import Product

class VaRBasket:

	def __init__(self, tsar_list: List[TsarDataStream], products: List[Product], weights: List[float]):
		assert len(tsar_list) == len(products), \
			f"len(Tsar) != len(Products) == {len(tsar_list)} != {len(products)}"
		assert len(weights) == len(products), \
			f"len(Weights) != len(Products) == {len(weights)} != {len(products)}"

		self.tsar_list = tsar_list
		self.weights = np.array(weights)

		self.dataframe = pd.DataFrame({
			product.name: product.get_close_series() for product in products
		}).ffill()
		self.last_prices = np.array([p.datastream.get_close_series().iat[-1] for p in products])
		self.block_size_vect = np.array([p.block_size for p in products])
		self.export_filenames = [p.name for p in products]

		self.S0 = self.dataframe.iloc[-1].to_numpy()
		self.tails = self.dataframe.tail(10).values.T
		self.pct_returns = self.dataframe.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
		self.mu = np.array(self.pct_returns.mean(axis=0))
		self.std = np.array(self.pct_returns.std(axis=0))

	def simulate_hist(self, n_days, sample_ratio: float):
		Z = np.sqrt(n_days) * self.pct_returns.sample(frac=sample_ratio, axis=0)
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
		e = np.exp(drift[:, np.newaxis] + vol)

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

	def monte_carlo_VaR_vect(self, alpha: float, n_days: int = 1, n_simulation: int = 100000, gen_path: bool = True):
		pose_vect = np.array([tsar.last_pose() for tsar in self.tsar_list])
		pose_block_size = np.einsum("i,i->i", pose_vect, self.block_size_vect)

		if gen_path:
			P = np.array(self.simulate_price_paths(n_days, n_simulation))
			daily_diff = np.diff(P, axis=2)
			returns = np.einsum("i,ijk->ij", pose_block_size, daily_diff)
		else:  # single
			generated_prices = self.simulate_price(n_days, n_simulation)
			generated_price_diff = generated_prices - self.last_prices[:, np.newaxis]
			returns = np.einsum("i,ij->ij", pose_block_size, generated_price_diff)

		return [np.quantile(np.sort(p), alpha) for p in returns]

	def histo_VaR_vect(self, alpha: float, n_days: int = 1, sample_ratio: float = 0.6, gen_path: bool = True):
		pose_vect = np.array([tsar.last_pose() for tsar in self.tsar_list])
		pose_block_size = np.einsum("i,i->i", pose_vect, self.block_size_vect)

		if gen_path:
			P = np.array(self.simulate_hist_paths(n_days, sample_ratio))
			daily_diff = np.diff(P, axis=2)
			returns = np.einsum("i,ijk->ij", pose_block_size, daily_diff)
		else:  # single
			generated_prices = self.simulate_hist(n_days, sample_ratio)
			generated_price_diff = generated_prices - self.last_prices[:, np.newaxis]
			returns = np.einsum("i,ij->ij", pose_block_size, generated_price_diff)

		return [np.quantile(np.sort(p), alpha) for p in returns]
