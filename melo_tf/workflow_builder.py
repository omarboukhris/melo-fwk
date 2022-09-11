
from helpers import config
from dataclasses import dataclass
from process.policies import vol_target_policy
from typing import List
from copy import deepcopy

from quantfactory_registry import quantflow_factory


@dataclass(frozen=True)
class WorkflowBuilder:
	workflow_config: config.WorkflowConfig

	def build(self):
		product_ds = self.get_product_datastream(self.workflow_config.product)
		strategies = self.get_strategies(self.workflow_config.strategy)
		sizepolicy = self.get_size_policy(
			self.workflow_config.vol_target,
			self.workflow_config.size_policy,
		)
		#get workflow by type (ex: backtest)
		#init with parsed data and return, run should be done outside

		#start with backtest (simple full wkflow),
		#then universe selection, strategy optimization,
		#portfolio allocation and risk management

		# testing options : roll out of sample (param: lookback)

	def get_product_datastream(self, product_query: dict):
		print(self.workflow_config.product)
		return {}

	def get_strategies(self, strategy_query: List[dict]):
		output_strategies = []
		for strategy in self.workflow_config.strategy:
			strat = deepcopy(strategy)
			StrategyClass = quantflow_factory.QuantFlowFactory.strategies[strat["type"]]
			del strat["type"]
			output_strategies.append(StrategyClass(**strat))
		return output_strategies

	def get_size_policy(self, vol_target_query: dict, size_policy_query: str):
		vol_target = vol_target_policy.VolTarget(**vol_target_query)
		size_policy = quantflow_factory.QuantFlowFactory.size_policies[size_policy_query](vol_target)
		return size_policy



"""

parse config
init workflow builder with parsed config
run generated workflow
output will be raw data :
	- orderbook
	- some stats
	- pnl
	- drawdown...
should code something like an output formatter

"""

"""
For cov_mat and portfolio opt:
	default strategy buy and hold (const 0 < forcast)
	default size policy const (0 < size) -> null voltarget

"""


