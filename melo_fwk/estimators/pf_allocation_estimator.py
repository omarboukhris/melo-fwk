from typing import List

import pandas as pd
import tqdm

from melo_fwk.estimators.utils.weights_optim import WeightsOptim
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.utils.weights import Weights


class PFAllocationEstimator:

	def __init__(
		self,
		trading_syst_list: List[BaseTradingSystem],
		weights: Weights,
		estimator_params: List[str]
	):
		self.trading_syst_list = trading_syst_list
		self.weights = weights
		self.estimator_params = iter(estimator_params)
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
		for trading_sys in tqdm.tqdm(self.trading_syst_list, leave=False):
			trading_results = trading_sys.run()
			optim_df = PFAllocationEstimator.optimize_weights_by_cluter(trading_results)

			out_dict[trading_sys.name] = optim_df
			mean_div_mult = optim_df["DivMult"].mean()
			mean_weights = optim_df["OptimResult.x"].mean()
			weights = mean_weights * mean_div_mult

			weighted_results = trading_results.apply_weights(weights)
			acc_trading_sys[trading_sys.name] = weighted_results.accumulate("Account")

		self.logger.info("Running estimator on portfolio")
		pf_optim_results = []
		window_size, min_periods, step = 250, 250, 20
		indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=window_size)
		for rolling_tr in acc_trading_sys.rolling(window=indexer, min_periods=min_periods, step=step):
			pf_optim_results.append(
				PFAllocationEstimator.run_weights_optim(rolling_tr))

		self.logger.info("Finished running estimator")
		return out_dict, pd.DataFrame(pf_optim_results)

	@staticmethod
	def optimize_weights_by_cluter(trading_results):
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




