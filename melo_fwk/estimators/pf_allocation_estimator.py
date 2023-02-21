from typing import List

import numpy as np
import pandas as pd
import tqdm

from melo_fwk.basket.var_basket import VaRBasket
from melo_fwk.estimators.utils.var_utils import VaRUtils
from melo_fwk.estimators.utils.weights_optim import WeightsOptim
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.utils.weights import Weights
from melo_fwk.var.CVaR import CVaR_vect
from melo_fwk.var.VaR import VaR99_vect


class PFAllocationEstimator:

	def __init__(
		self,
		trading_syst_list: List[BaseTradingSystem],
		weights: Weights,
		estimator_params: List[str]
	):
		self.begin, self.end = None, None
		self.trading_syst_list = trading_syst_list
		self.weights = weights
		self.estimator_params = iter(estimator_params)
		self.n_days = self.next_int_param(1)
		self.method = self.next_str_param("mc")
		self.sim_param = self.next_int_param(1000) if self.method == "mc" else self.next_float_param(0.8)
		self.gen_path = self.next_int_param(0) != 0
		self.logger = GlobalLogger.build_composite_for(
			PFAllocationEstimator.__name__)

	def next_str_param(self, default_val):
		try:
			return next(self.estimator_params)
		except StopIteration:
			return default_val

	def next_int_param(self, default_val):
		return int(self.next_str_param(default_val))

	def next_float_param(self, default_val):
		return float(self.next_str_param(default_val))

	def run(self):
		"""
		run weights optim on 2 levels:
			clusters
			portfolio
		run rolling VaR on portfolio level
		run vol target on portfolio ?
		:return:
		"""
		out_dict = dict()
		acc_trading_sys = pd.DataFrame({})
		n = len(self.trading_syst_list)
		self.logger.info(f"Running Estimatior on {n} clusters")
		cluster_weights = []
		for trading_sys in tqdm.tqdm(self.trading_syst_list, leave=False):
			trading_results = trading_sys.run()
			optim_df = PFAllocationEstimator.optimize_weights_by_cluster(trading_results)

			out_dict[trading_sys.name] = optim_df
			mean_div_mult = optim_df["DivMult"].mean()
			mean_weights = optim_df["OptimResult.x"].mean()
			weights = mean_weights * mean_div_mult
			cluster_weights.append(weights)

			weighted_results = trading_results.apply_weights(weights)
			acc_trading_sys[trading_sys.name] = weighted_results.accumulate("Account")

		self.logger.info("Running estimator on portfolio")
		pf_optim_results = []
		window_size, min_periods, step = 250, 250, 20
		indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=window_size)
		for rolling_tr in acc_trading_sys.rolling(window=indexer, min_periods=min_periods, step=step):
			pf_optim_results.append(
				PFAllocationEstimator.run_weights_optim(rolling_tr))

		# apply pf weights to positions in rolling_weighted_results
		pf_optim_results = pd.DataFrame(pf_optim_results)
		prod_list = [ts.product_basket for ts in self.trading_syst_list]
		var_profiles, weights = [], []
		mean_div_mult = pf_optim_results["DivMult"].mean()
		for i in range(len(prod_list)):
			mean_weights = pf_optim_results["OptimResult.x"].mean()[i]
			weights_i = mean_weights * mean_div_mult * cluster_weights[i]
			weights.append(weights_i)

		for trading_sys, products_basket, w_i in tqdm.tqdm(zip(self.trading_syst_list, prod_list, weights)):
			var_utils = VaRUtils(trading_subsys=trading_sys, products=products_basket.products, weights=w_i)
			var_utils.set_VaR_params(self.n_days, self.method, self.sim_param, self.gen_path)
			# add begin...end parsing in mql pf alloc rule
			self.begin, self.end = min(products_basket.years()), max(products_basket.years())
			var_profiles.append(var_utils.run_full_VaR_sim(self.begin, self.end))

		self.logger.info("Finished running estimator")
		return out_dict, pd.DataFrame(pf_optim_results).mean(numeric_only=False), var_profiles, weights

	@staticmethod
	def optimize_weights_by_cluster(trading_results):
		optim_results = []

		for rolling_tr in tqdm.tqdm(trading_results.rolling("Account"), leave=False):
			optim_results.append(
				PFAllocationEstimator.run_weights_optim(rolling_tr))

		return pd.DataFrame(optim_results)

	@staticmethod
	def run_weights_optim(rolling_tr):
		n = len(rolling_tr.T)
		base_weights = [1/n] * n
		opt_result, div_mult = WeightsOptim.optimize_weights(
			rolling_tr.mean(axis=0), rolling_tr, base_weights
		)
		return {
			"OptimResult.fun": opt_result.fun,
			"OptimResult.x": opt_result.x,
			"DivMult": div_mult
		}




