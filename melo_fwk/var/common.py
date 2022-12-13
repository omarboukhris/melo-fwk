from cmath import sqrt
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.stats import norm


"""
methods : 
	parametric
	histo
	MC

scenarios :
	VaR - 95 & 99
	CVaR - ES
	SVaR

Check VaR and adjust size accordingly. 
"""

def VaRFactory(var_type: str = "monte_carlo"):
	if var_type == "param":
		return ParametricVar
	if var_type == "histo":
		return HistVar
	if var_type == "monte_carlo":
		return MonteCarloVar

@dataclass(frozen=False)
class BaseVaR:
	alpha: float
	n_days: int = 1

	def __call__(self, returns: pd.DataFrame, method: str = "gbm"):
		pass

	def set_sample_param(self, sample_param):
		pass


@dataclass(frozen=False)
class ParametricVar(BaseVaR):

	def __call__(self, returns: pd.DataFrame, method: str = None):
		S0 = returns.iloc[-1].to_numpy()
		pct_returns = returns.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
		mu = pct_returns.mean(axis=0)
		std = pct_returns.std(axis=0)
		Z = np.sqrt(self.n_days) * norm.ppf(self.alpha, mu, std)
		return pd.DataFrame(S0 * Z).fillna(0).to_numpy()


@dataclass(frozen=False)
class HistVar(BaseVaR):
	sample_ratio: float = 0.3

	def __call__(self, returns: pd.DataFrame, method: str = "gbm"):
		"""TODO:
			solve bug :  return ratio seems too small, figure out the right one
			Pi+1 = (1 + r_ij) Pi
		"""
		S0 = returns.iloc[-1].to_numpy()
		pct_returns = returns.pct_change(axis=0).replace([np.inf, -np.inf], np.nan).dropna()
		Z = np.sqrt(self.n_days) * pct_returns.sample(frac=self.sample_ratio, axis=0)
		e = 1 + Z
		P = np.nan_to_num(S0 * e).T

		# if method == "sim_path":
		# 	Z = [pct_returns.sample(frac=self.sample_ratio, axis=0) for _ in range(self.n_days)]
		# 	e = 1 - np.exp(np.sum(Z, 0))
		# 	P = np.nan_to_num(S0 * e).sum(axis=2)[-1]
		#
		# else:  # single_sim
		# 	Z = np.array([returns.sample(frac=self.sample_ratio) for _, returns in pct_returns.items()])
		# 	e = 1 - np.exp(Z)
		# 	P = np.sqrt(self.n_days) * np.nan_to_num(S0 * Z.T).sum(axis=1)

		return np.array([
			pd.Series(p).sort_values(ascending=True).quantile(self.alpha)
			for p in P
		])

	def set_sample_param(self, sample_param):
		self.sample_ratio = sample_param


@dataclass(frozen=False)
class MonteCarloVar(BaseVaR):
	n_simulation: int = 1e+5

	def __call__(self, returns: pd.DataFrame, method: str = "gbm"):
		# nice demo :
		# https://math.stackexchange.com/questions/163470/generating-correlated-random-numbers-why-does-cholesky-decomposition-work
		S0 = returns.iloc[-1].to_numpy()
		pct_returns = returns.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
		mu = np.array(pct_returns.mean(axis=0))
		std = np.array(pct_returns.std(axis=0))
		corr_mat = pct_returns.corr().fillna(0)
		L = np.linalg.cholesky(corr_mat.to_numpy())

		if method == "sim_path":
			Z = np.array([
				(mu - std ** 2 / 2) + std * np.matmul(
					L, norm.rvs(size=[len(corr_mat.columns), self.n_simulation])).T
				for _ in range(self.n_days)
			])
			e = np.exp(np.sum(Z, 0))
			P = np.nan_to_num(S0[:, np.newaxis] * e.T)

		else:  # single_sim
			Z = np.matmul(L, norm.rvs(size=[len(corr_mat.columns), self.n_simulation])).T
			e = np.exp((mu - std ** 2 / 2) * self.n_days + std * np.sqrt(self.n_days) * Z)
			P = np.nan_to_num(S0[:, np.newaxis] * e.T)

		return np.array([
			pd.Series(p).sort_values(ascending=True).quantile(self.alpha)
			for p in P
		])

	def set_sample_param(self, sample_param):
		self.n_simulation = sample_param
