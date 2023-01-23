
import json
import glob
from typing import List

from melo_fwk.basket.strat_basket import StratBasket
from melo_fwk.utils.weights import Weights


class QuantFlowFactory:

	products = dict()
	strategies = dict()
	strat_configs = dict()
	search_spaces = dict()
	estimators = dict()
	reporters = dict()
	size_policies = dict()
	result_writers = dict()

	@staticmethod
	def register_product(product_label: str, product: tuple):
		QuantFlowFactory.products[product_label] = product

	@staticmethod
	def get_product(product_label: str):
		return QuantFlowFactory.products[product_label]

	@staticmethod
	def register_strategy(strategy_label: str, strategy: callable):
		QuantFlowFactory.strategies[strategy_label] = strategy

	@staticmethod
	def get_strategy(strategy_label: str):
		return QuantFlowFactory.strategies[strategy_label]

	@staticmethod
	def register_search_space(search_space_label: str, search_space):
		QuantFlowFactory.search_spaces[search_space_label] = search_space

	@staticmethod
	def get_search_space(search_space_label: str):
		return QuantFlowFactory.search_spaces[search_space_label]

	@staticmethod
	def register_size_policy(size_policy_label: str, size_policy: callable):
		QuantFlowFactory.size_policies[size_policy_label] = size_policy

	@staticmethod
	def get_size_policy(size_policy_label: str):
		return QuantFlowFactory.size_policies[size_policy_label]

	@staticmethod
	def register_estimator(estimator_label: str, estimator: callable):
		QuantFlowFactory.estimators[estimator_label] = estimator

	@staticmethod
	def get_estimator(estimator_label: str):
		return QuantFlowFactory.estimators[estimator_label]

	@staticmethod
	def register_reporter(estimator_label: str, reporter: callable):
		QuantFlowFactory.reporters[estimator_label] = reporter

	@staticmethod
	def get_reporter(estimator_label: str):
		return QuantFlowFactory.reporters[estimator_label]

	@staticmethod
	def get_result_writer(result_writer_label: str):
		return QuantFlowFactory.result_writers[result_writer_label]

	@staticmethod
	def register_strat_configs(filepath: str):
		config_files = glob.glob(filepath)
		for config_file in config_files:
			json_config = json.loads(config_file)
			QuantFlowFactory.strat_configs[config_file] = json_config

	@staticmethod
	def get_strat_configs(config_file: str):
		return QuantFlowFactory.strat_configs[config_file]

	@classmethod
	def build_strat_basket(cls, strat_basket_config: dict):
		strat_list = [
			QuantFlowFactory.get_strategy(strat_name)(**config)
			for strat_name, config in strat_basket_config["strat_list"].items()
		]
		weights = Weights(**strat_basket_config["weights"])
		return StratBasket(strat_list, weights)
