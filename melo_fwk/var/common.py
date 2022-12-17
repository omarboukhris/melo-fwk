
import numpy as np

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
