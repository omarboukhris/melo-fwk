import numpy as np
import pandas as pd
import tqdm

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.strat_basket import StratBasket
from melo_fwk.basket.var_basket import VaRBasket
from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.var.CVaR import CVaR, CVaR_vect
from melo_fwk.var.VaR import VaR99, VaR99_vect


class VaREstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(VaREstimator, self).__init__(**kwargs)
		self.logger.info("VaREstimator Initialized")

		self.n_days = self.next_int_param(1)
		self.method = self.next_str_param("mc")
		self.sim_param = self.next_int_param(1000) if self.method == "mc" else self.next_float_param(0.8)
		self.gen_path = self.next_int_param(0) != 0

	def run(self):

		self.logger.info(f"Running Estimatior on {len(self.products)} Products")
		strat_basket = StratBasket(
			strat_list=self.strategies,
			weights=self.forecast_weights,
		)
		trading_subsys = TradingSystem(
			strat_basket=strat_basket,
			size_policy=self.size_policy
		)

		var_params = f"Params = [ndays={self.n_days}, sim_param={self.sim_param}, method={self.method}, gen_path={self.gen_path}"

		window_size, min_period, step = 250, 250, 20
		years = list(range(self.begin, self.end))
		prd_map, tsar_map, min_len = {}, {}, np.inf
		for product_name, product in self.products.items():
			prd_map[product_name] = []
			tsar_map[product_name] = []

			for i, prd in tqdm.tqdm(enumerate(product.rolling(years, window_size, min_period, step)), leave=False):
				tsar = trading_subsys.run_product(prd)
				prd_map[product_name].append(prd)
				tsar_map[product_name].append(tsar)

			min_len = min(min_len, len(prd_map[product_name]))

			self.logger.info(f"Simulation for product {product_name} Done")

		prd_map = {k: v[:min_len] for k, v in prd_map.items()}
		tsar_map = {k: v[:min_len] for k, v in tsar_map.items()}

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

		self.logger.info(f"Product and Returns maps built")
		self.logger.info(f"Computing VaR with VaR Params = {var_params}")

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

		self.logger.info("Finished running estimator")

		return out_dict

