from cmath import sqrt
from dataclasses import dataclass

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

	def simulate_prices(
		self, S0, Z,
		returns: pd.DataFrame,
		weights: np.array,
		method: str = "gbm"
	):
		wS0 = np.array(S0.multiply(weights))

	def get_alpha_sensi(self, P):
		index = int(self.alpha*len(P))
		return pd.Series(P).sort_values(ascending=True).iat[index]

	def __call__(self, returns: pd.DataFrame, weights: np.array, method: str = "gbm"):
		pass

	def set_sample_param(self, sample_param):
		pass


@dataclass(frozen=False)
class ParametricVar(BaseVaR):

	def __call__(self, returns: pd.DataFrame, weights: np.array, method: str = None):
		S0 = returns.iloc[-1]
		pct_returns = returns.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
		mu = weights.T @ pct_returns.mean(axis=0)
		std = np.sqrt(weights.T @ pct_returns.cov() @ weights)
		Z = norm.ppf(self.alpha, mu, std)
		wS0 = np.array(S0.multiply(weights))
		P = np.sqrt(self.n_days) * (wS0[..., np.newaxis] * Z)

		return np.float64(P)

@dataclass(frozen=False)
class HistVar(BaseVaR):
	sample_ratio: float = 0.3

	def __call__(self, returns: pd.DataFrame, weights: np.array, method: str = "gbm"):
		"""TODO:
			solve bug :  return ratio seems too small, figure out the right one
			looks like it half its correct value
			OR
			rework without GBM, Pi+1 = (1 + r_ij) Pi
		"""
		S0 = returns.iloc[-1]
		wS0 = np.array(S0.multiply(weights))
		pct_returns = returns.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
		n_sample = int(len(pct_returns)*self.sample_ratio)
		if method == "sim_path":
			Z = np.cumsum([pct_returns.sample(n=n_sample).T for _ in range(self.n_days)], 0)
			P = (wS0[..., np.newaxis] * Z).sum(axis=1)[-1]

		else:  # sim_path
			Z = np.array(pct_returns.sample(n=n_sample).T)
			P = np.sqrt(self.n_days) * (wS0[..., np.newaxis] * Z).sum(axis=0)
		# P = self.simulate_prices(S0, Z, pct_returns, weights, method)

		return self.get_alpha_sensi(P)

	def set_sample_param(self, sample_param):
		self.sample_ratio = sample_param


@dataclass(frozen=False)
class MonteCarloVar(BaseVaR):
	n_simulation: int = 1e+5

	def __call__(self, returns: pd.DataFrame, weights: np.array, method: str = "gbm"):
		# nice demo :
		# https://math.stackexchange.com/questions/163470/generating-correlated-random-numbers-why-does-cholesky-decomposition-work
		S0 = returns.iloc[-1]
		wS0 = np.array(S0.multiply(weights))
		pct_returns = returns.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
		mu = np.array(pct_returns.mean(axis=0))
		std = np.array(pct_returns.std(axis=0))
		corr_mat = pct_returns.corr().fillna(0)
		L = np.linalg.cholesky(corr_mat.to_numpy())

		if method == "sim_path":
			Z = np.array([
				np.matmul(L, norm.rvs(size=[len(corr_mat.columns), self.n_simulation]))
				for _ in range(self.n_days)
			])
			e = 1 - np.exp(np.cumsum((mu - std ** 2 / 2) + std * Z, 0))
			P = np.nan_to_num(wS0[:, np.newaxis] * e).sum(axis=1)[-1]

		else:  # single_sim
			Z = np.matmul(L, norm.rvs(size=[len(corr_mat.columns), self.n_simulation]))
			e = 1 - np.exp((mu - std ** 2 / 2) * self.n_days + std * np.sqrt(self.n_days) * Z)
			P = np.nan_to_num(wS0[:, np.newaxis] * e).sum(axis=0)

		return self.get_alpha_sensi(P)

	def set_sample_param(self, sample_param):
		self.n_simulation = sample_param
