import numpy as np
import pandas as pd
import tqdm

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.strat_basket import StratBasket
from melo_fwk.basket.var_basket import VaRBasket
from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.estimators.utils.var_utils import VaRUtils
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.var.CVaR import CVaR, CVaR_vect
from melo_fwk.var.VaR import VaR99, VaR99_vect


class VaREstimator(MeloBaseEstimator):

	def __init__(self, **kwargs):
		super(VaREstimator, self).__init__(**kwargs)
		self.n_days = self.next_int_param(1)
		self.method = self.next_str_param("mc")
		self.sim_param = self.next_int_param(1000) if self.method == "mc" else self.next_float_param(0.8)
		self.gen_path = self.next_int_param(0) != 0
		self.logger.info("VaREstimator Initialized")


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

		var_utils = VaRUtils(trading_subsys, self.products)

		self.logger.info(f"Running simulations for {len(self.products.values())} products from {self.begin} to {self.end}")
		sim_results = var_utils.run_simulations(self.begin, self.end)
		self.logger.info(f"Product and Returns maps built")

		var_params = f"Params=[ndays={self.n_days},sim_param={self.sim_param},method={self.method}, gen_path={self.gen_path}]"
		self.logger.info(f"Computing VaR with VaR Params = {var_params}")
		var_utils.set_VaR_params(self.n_days, self.method, self.sim_param, self.gen_path)

		out_dict = var_utils.get_risk_profile(*sim_results)
		self.logger.info("Finished running estimator")

		return out_dict

