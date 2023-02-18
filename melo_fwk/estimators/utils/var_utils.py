from typing import Union

import numpy as np
import pandas as pd
import tqdm

from melo_fwk.basket.var_basket import VaRBasket
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.var.CVaR import CVaR_vect
from melo_fwk.var.VaR import VaR99_vect


class VaRUtils:

	def __init__(self, trading_subsys: BaseTradingSystem, products: dict):
		self.trading_subsys = trading_subsys
		self.products = products

		self.n_days = 0
		self.method = None
		self.sim_param = 0
		self.gen_path = False

	def set_VaR_params(self, n_days: int, method: str, sim_param: Union[float, int], gen_path: bool):
		self.n_days = n_days
		self.method = method
		self.sim_param = sim_param
		self.gen_path = gen_path

	def run_simulations(self, begin: int, end: int):
		"""
		:param products:
		:param begin:
		:param end:
		:return:
			prd_map : dict, product name -> list(rolling products)
			tsar_map : dict, product name -> list(rolling tsars)
			min_len : common minimum length between products
		"""

		window_size, min_period, step = 250, 250, 20
		years = list(range(begin, end))
		prd_map, tsar_map, min_len = {}, {}, np.inf
		for product_name, product in self.products.items():
			prd_map[product_name] = []
			tsar_map[product_name] = []

			for i, prd in tqdm.tqdm(enumerate(product.rolling(years, window_size, min_period, step)), leave=False):
				tsar = self.trading_subsys.run_product(prd)
				prd_map[product_name].append(prd)
				tsar_map[product_name].append(tsar)

			min_len = min(min_len, len(prd_map[product_name]))

		prd_map = {k: v[:min_len] for k, v in prd_map.items()}
		tsar_map = {k: v[:min_len] for k, v in tsar_map.items()}

		return prd_map, tsar_map, min_len

	def get_risk_profile(self, prd_map: dict, tsar_map: dict, min_len: int):
		out_dict = {
			product_name: pd.DataFrame({
				"idx": [],
				"var99": [],
				"cvar": [],
				"var99_rand_shock_20_5": [],
				"cvar_rand_shock_20_5": []
			})
			for product_name in self.products.keys()
		}

		for i in tqdm.tqdm(range(min_len), leave=False):
			tsar = [t[i] for t in tsar_map.values()]
			prd = [p[i] for p in prd_map.values()]
			# Note: could be dangerous to use product subset in varbasket
			# there won't be much data to model returns (1 year)
			# maybe use whole product ??
			# NOTE: dump tsar df to markdown as report annex
			# TODO: add 10 days VaR (hist path) and shocked 10 days VaR (MC path)
			var_basket = VaRBasket(tsar, prd)
			var99_vect = VaR99_vect(var_basket, self.n_days, self.sim_param, self.method, self.gen_path)
			cvar_vect = CVaR_vect(var_basket, self.n_days, self.sim_param, self.method, self.gen_path)

			var_basket.random_vol_shock(0.2, 0.05)
			var99_rsh_20_5_vect = VaR99_vect(var_basket, self.n_days, self.sim_param, self.method, self.gen_path)
			cvar_rsh_20_5_vect = CVaR_vect(var_basket, self.n_days, self.sim_param, self.method, self.gen_path)
			var_basket.reset_vol()

			loop_args = out_dict.keys(), var99_vect, cvar_vect, var99_rsh_20_5_vect, cvar_rsh_20_5_vect
			for k, var99, cvar, var99_rand_shock_20_5, cvar_rand_shock_20_5 in zip(*loop_args):
				out_dict[k] = pd.concat([out_dict[k], pd.DataFrame({
					"idx": [i],
					"var99": [var99],
					"cvar": [np.mean(cvar)],
					"var99_rand_shock_20_5": [var99_rand_shock_20_5],
					"cvar_rand_shock_20_5": [np.mean(cvar_rand_shock_20_5)]
				})])

		return out_dict
