from cmath import sqrt
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from scipy.stats import norm

from melo_fwk.var.basket import VaRBasket

"""
methods : 
	histo
	MC

scenarios :
	VaR - 95 & 99
	CVaR - ES

todo: SVaR

Strat : Check VaR and adjust size accordingly. 
"""

def simpleVaR(
	alpha: float,
	basket: VaRBasket,
	n_days: int,
	sample_param,
	method: str = "monte_carlo",
	gen_path: bool = True,
	full_sum: bool = True
):
	if method in ["monte_carlo", "mc"]:
		var_vect = basket.monte_carlo_VaR_vect(
			alpha=alpha,
			n_days=n_days,
			n_simulation=sample_param,
			gen_path=gen_path,
		)
	else:  # method in ["histo", "h"]
		var_vect = basket.histo_VaR_vect(
			alpha=alpha,
			n_days=n_days,
			sample_ratio=sample_param,
			gen_path=gen_path,
		)

	ein_symb = "i,i" if full_sum else "i,i->i"
	return np.einsum(ein_symb, var_vect, basket.weights)

def expected_shortfall(
	alpha: float,
	basket: VaRBasket,
	n_days: int,
	sample_param,
	method: str = "monte_carlo",
	gen_path: bool = True,
	nbins: int = 100
):
	var_list = []
	step_size = alpha / nbins
	alpha = step_size

	for i in range(nbins):
		var = simpleVaR(alpha, basket, n_days, sample_param, method, gen_path, full_sum=True)
		var_list.append(var)
		alpha += step_size

	return np.array(var_list)

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
	"""OUTDATED"""

	def __call__(self, returns: pd.DataFrame, method: str = None):
		S0 = returns.iloc[-1].to_numpy()
		pct_returns = returns.pct_change().replace([np.inf, -np.inf], np.nan).dropna()
		mu = pct_returns.mean(axis=0)
		std = pct_returns.std(axis=0)
		Z = np.sqrt(self.n_days) * norm.ppf(self.alpha, mu, std)
		return pd.DataFrame(S0 * Z).fillna(0).to_numpy()
