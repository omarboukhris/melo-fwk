
import json, glob

class QuantFlowFactory:

	products = dict()
	strategies = dict()
	strat_configs = dict()
	workflows = dict()
	size_policies = dict()
	result_writers = dict()

	@staticmethod
	def register_product(product_label: str, product: tuple):
		QuantFlowFactory.products[product_label] = product

	@staticmethod
	def register_strategy(strategy_label: str, strategy: callable):
		QuantFlowFactory.strategies[strategy_label] = strategy

	@staticmethod
	def register_workflow(workflow_label: str, workflow: callable):
		QuantFlowFactory.workflows[workflow_label] = workflow

	@staticmethod
	def register_size_policy(size_policy_label: str, size_policy: callable):
		QuantFlowFactory.size_policies[size_policy_label] = size_policy

	@staticmethod
	def register_result_writer(result_writer_label: str, result_writer: callable):
		QuantFlowFactory.result_writers[result_writer_label] = result_writer

	@staticmethod
	def register_strat_configs(filepath: str):
		config_files = glob.glob(filepath)
		for config_file in config_files:
			json_config = json.loads(config_file)
			QuantFlowFactory.strat_configs[config_file] = json_config
