import pandas as pd
import tqdm

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.start_basket import StratBasket
from melo_fwk.basket.var_basket import VaRBasket
from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.var.CVaR import CVaR
from melo_fwk.var.VaR import VaR99


class VaREstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(VaREstimator, self).__init__(**kwargs)
		self.logger.info("VaREstimator Initialized")

		self.n_days = self.next_int_param(1)
		self.method = self.next_str_param("mc")
		self.sim_param = self.next_int_param(1000) if self.method == "mc" else self.next_float_param(0.8)
		self.gen_path = self.next_int_param(0) != 0

	def run(self):
		out_dict = {
			"year": [],
			"var99": [],
			"cvar": [],
			"var99_rand_shock_20_5": [],
			"cvar_rand_shock_20_5": []
		}
		var_basket_map = {}

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

		for year in range(self.begin, self.end):
			prd_list, tsar_list = [], []
			for i, (product_name, product) in tqdm.tqdm(enumerate(self.products.items()), leave=False):
				tsar = trading_subsys.run_product_year(product, year)
				prd_list.append(product.get_year(year))
				tsar_list.append(tsar)

			self.logger.info(f"Simulation year {year} Done, Computing VaR with params :")
			self.logger.info(var_params)

			var_basket = VaRBasket(tsar_list, prd_list)
			var_basket_map[year] = var_basket
			var99 = VaR99(var_basket, self.n_days, self.sim_param, self.method, self.gen_path)
			cvar = CVaR(var_basket, self.n_days, self.sim_param, self.method, self.gen_path)

			var_basket.reset_vol().random_vol_shock(0.2, 0.05)
			var99_rand_shock_20_5 = VaR99(var_basket, self.n_days, self.sim_param, self.method, self.gen_path)
			cvar_rand_shock_20_5 = CVaR(var_basket, self.n_days, self.sim_param, self.method, self.gen_path)
			var_basket.reset_vol()

			out = f"\nVaR99 = {var99} | {var_params}\n"
			out += f"CVaR = {cvar} | {var_params}\n"
			out += f"VaR99 w/ random shock 20+-5 = {var99_rand_shock_20_5} | {var_params}\n"
			out += f"CVaR w/ random shock 20+-5 = {cvar_rand_shock_20_5} | {var_params}\n"

			out_dict["year"].append(year)
			out_dict["var99"].append(var99)
			out_dict["cvar"].append(cvar)
			out_dict["var99_rand_shock_20_5"].append(var99_rand_shock_20_5)
			out_dict["cvar_rand_shock_20_5"].append(cvar_rand_shock_20_5)

			self.logger.info(out)

		self.logger.info("Finished running estimator")
		return (
			pd.DataFrame(out_dict),
			var_basket_map,
			(self.method, (self.n_days, self.sim_param))
		)

