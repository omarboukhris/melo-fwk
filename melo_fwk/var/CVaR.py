
from melo_fwk.var.basket import VaRBasket
from melo_fwk.var.common import expected_shortfall

def CVaR(
	basket: VaRBasket,
	n_days: int,
	sample_param,
	method: str = "monte_carlo",
	gen_path: bool = True,
	nbins: int = 100
):
	return expected_shortfall(0.01, basket, n_days, sample_param, method, gen_path, nbins).mean()

def CVaR_vect(
	basket: VaRBasket,
	n_days: int,
	sample_param,
	method: str = "monte_carlo",
	gen_path: bool = True,
	nbins: int = 100
):
	return expected_shortfall(0.01, basket, n_days, sample_param, method, gen_path, nbins)
