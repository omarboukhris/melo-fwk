from typing import List

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
		self.estimator_params = estimator_params

	def run(self):
		"""
		run weights optim on 2 levels:
			clusters
			portfolio
		run rolling VaR on portfolio level
		run vol target on portfolio ?
		:return:
		"""
