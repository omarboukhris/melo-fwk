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
	SVaR - FRTB

Check VaR and adjust size accordingly. 
What should be the formula??
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

	def simulate_prices(self, Z, returns: pd.DataFrame, weights: np.array, method: str = "gbm_path"):
		if method == "linear":
			return sqrt(self.n_days) * Z * returns.iat[-1]
		else:  # GBM models
			mu = weights.T @ returns
			std = np.sqrt(weights.T @ returns.cov() @ weights)
			if method == "gbm":
				return returns.iat[-1] * np.exp(mu * self.n_days + std * sqrt(self.n_days) * Z)
			elif method == "gbm_path":
				return returns.iat[-1] * np.exp(np.cumsum(mu + std * Z))

	def get_alpha_sensi(self, P):
		index = int(self.alpha*len(P))
		return P.sort_values().iat[index]

	def __call__(self, returns: pd.DataFrame, weights: np.array, method: str = "gbm_path"):
		pass

	def set_sample_param(self, sample_param):
		pass


@dataclass(frozen=False)
class ParametricVar(BaseVaR):

	def __call__(self, returns: pd.DataFrame, weights: np.array, method: str = "gbm_path"):
		pct_returns = returns.diff()/returns
		mu = weights.T @ pct_returns
		std = np.sqrt(weights.T @ pct_returns.cov() @ weights)
		Z = norm.ppf(self.alpha, mu, std)
		P = self.simulate_prices(Z, pct_returns, weights, method)

		return self.get_alpha_sensi(P)

@dataclass(frozen=False)
class HistVar(BaseVaR):
	sample_ratio: float = 0.3

	def __call__(self, returns: pd.DataFrame, weights: np.array, method: str = "gbm_path"):
		pct_returns = returns.diff()/returns
		n_sample = int(len(pct_returns)*self.sample_ratio)
		Z = pct_returns.sample(n=n_sample)
		P = self.simulate_prices(Z, pct_returns, weights, method)

		return self.get_alpha_sensi(P)

	def set_sample_param(self, sample_param):
		self.sample_ratio = sample_param


@dataclass(frozen=False)
class MonteCarloVar(BaseVaR):
	n_simulation: int = 1e+5

	def __call__(self, returns: pd.DataFrame, weights: np.array, method: str = "gbm_path"):
		# nice demo :
		# https://math.stackexchange.com/questions/163470/generating-correlated-random-numbers-why-does-cholesky-decomposition-work
		pct_returns = returns.diff()/returns
		cov_mat = pct_returns.cov()
		L = np.linalg.cholesky(cov_mat.to_numpy())
		Z = np.matmul(L, norm.rvs(size=[len(cov_mat.columns), self.n_simulation]))
		P = self.simulate_prices(Z, returns, weights, method)

		return self.get_alpha_sensi(P)

	def set_sample_param(self, sample_param):
		self.n_simulation = sample_param
