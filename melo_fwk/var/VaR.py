
from melo_fwk.basket.var_basket import VaRBasket
from melo_fwk.var.common import simpleVaR

def VaR99(basket: VaRBasket, n_days: int, sample_param, method: str = "monte_carlo", gen_path: bool = True):
	return simpleVaR(0.01, basket, n_days, sample_param, method, gen_path, True)

def VaR99_vect(basket: VaRBasket, n_days: int, sample_param, method: str = "monte_carlo", gen_path: bool = True):
	return simpleVaR(0.01, basket, n_days, sample_param, method, gen_path, False)

def VaR95(basket: VaRBasket, n_days: int, sample_param, method: str = "monte_carlo", gen_path: bool = True):
	return simpleVaR(0.05, basket, n_days, sample_param, method, gen_path, True)

def VaR95_vect(basket: VaRBasket, n_days: int, sample_param, method: str = "monte_carlo", gen_path: bool = True):
	return simpleVaR(0.05, basket, n_days, sample_param, method, gen_path, False)
