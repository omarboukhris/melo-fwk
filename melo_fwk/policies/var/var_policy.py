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

@dataclass(frozen=False)
class BaseVaR:
	alpha: float
	n_days: int = 1

	def __call__(self, returns: pd.Series):
		pass


# apply on whole portfolio, instead of account
# what should portfolio be ?? create portfolio class containing tsar list ?
@dataclass(frozen=False)
class ParametricVar(BaseVaR):

	def __call__(self, returns: pd.DataFrame):
		pct_returns = returns.diff()/returns
		# compute mu n std from pct_returns
		# return sqrt(self.n_days) * norm.ppf(self.alpha, mu, std) * returns.iat[-1]

@dataclass(frozen=False)
class HistVar(BaseVaR):
	sample_ratio: float = 0.3

	def __call__(self, returns: pd.DataFrame):
		pct_returns = returns.diff()/returns
		n_sample = int(len(pct_returns)*self.sample_ratio)
		Z = pct_returns.sample(n=n_sample)
		# linear model
		P = sqrt(self.n_days) * Z * returns.iat[-1]
		# GBM
		# get mu n std from returns df
		# p = returns.iat[-1] * np.exp(mu * self.n_days + std * sqrt(self.n_days) * returns_sample)
		# GBM price path
		# p = returns.iat[-1] * np.exp(np.cumsum(mu + std * Z))

		index = int(self.alpha*len(P))
		var = P.sort_values().iat[index]

@dataclass(frozen=False)
class MonteCarloVar(BaseVaR):
	n_simulation: int = 1e+5

	def __call__(self, returns: pd.DataFrame):
		pct_returns = returns.diff()/returns
		corr_mat = pct_returns.corr()
		L = np.linalg.cholesky(corr_mat.to_numpy())
		Z = np.matmul(L, norm.rvs(size=[len(corr_mat.columns), self.n_simulation]))
		# linear model
		P = sqrt(self.n_days) * Z * returns.iat[-1]
		# GBM
		# get mu n std from returns df
		# p = returns.iat[-1] * np.exp(mu * self.n_days + std * sqrt(self.n_days) * Z)
		# GBM price path
		# p = returns.iat[-1] * np.exp(np.cumsum(mu + std * Z))

		index = int(self.alpha*len(P))
		var = P.sort_values().iat[index]

