from cmath import sqrt
from dataclasses import dataclass

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
	SVaR - 

Check VaR and adjust size accordingly	
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

	def __call__(self, account: pd.Series):
		pct_returns = account.diff()/account
		return sqrt(self.n_days) * norm.ppf(self.alpha, pct_returns.mean(), pct_returns.std()) * account.iat[1]

@dataclass(frozen=False)
class HistVar(BaseVaR):
	sample_ratio: float = 0.3

	def __call__(self, account: pd.Series):
		pct_returns = account.diff()/account
		n_sample = int(len(pct_returns)*self.sample_ratio)
		returns_sample = pct_returns.sample(n=n_sample)
		p = sqrt(self.n_days) * returns_sample * account.iat[1]
		index = int(self.alpha*len(p))
		var = p.sort_values().iat[index]

@dataclass(frozen=False)
class MonteCarloVar(BaseVaR):
	n_simulation: int = 1e+5

	def __call__(self, returns: pd.Series):
		pass

