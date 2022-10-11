
from melo_fwk import quantfactory_registry
from melo_fwk.melo_config import \
	ConfigBuilderHelper, \
	ProductConfigBuilder, \
	StratConfigRegistry, \
	StrategyConfigBuilder, \
	SizePolicyConfigBuilder, \
	VolTargetConfigBuilder, \
	EstimatorConfigBuilder

from mql.mql_parser import MqlParser

from pathlib import Path


class MqlConfigBuilder:
	def __init__(self, quant_query_path: Path, quant_query: dict):
		self.products_config = ProductConfigBuilder.build_products(quant_query)
		self.size_policy_class_ = SizePolicyConfigBuilder.build_size_policy(quant_query)
		self.vol_target = VolTargetConfigBuilder.build_vol_target(quant_query)
		self.strat_config_registry = StratConfigRegistry(str(quant_query_path.parent))
		self.strategies_config = StrategyConfigBuilder.build_strategy(quant_query, self.strat_config_registry)
		self.estimator_config_ = EstimatorConfigBuilder.build_estimator(quant_query)

	def __str__(self):
		return str({
			"products": self.products_config,
			"size_policy": self.size_policy_class_,
			"vol_target": self.vol_target,
			"strat_config_registry": self.strat_config_registry,
			"strategies_config": self.strategies_config,
			"estimator_config": self.estimator_config_
		})

class MqlProcess:

	def __init__(self, mql_query_path: Path):
		self.mql_query_path = mql_query_path

		quantfactory_registry.register_all()

		mql_parser = MqlParser()
		parsed_mql = mql_parser.parse_to_json(str(self.mql_query_path))
		quant_query = ConfigBuilderHelper.strip_single(parsed_mql, "QuantQuery")

		self.mql_config = MqlConfigBuilder(
			quant_query_path=self.mql_query_path,
			quant_query=quant_query
		)

	def run_process(self):
		estimator_obj_ = self.mql_config.estimator_config_[0](
			products=self.mql_config.products_config[0],
			time_period=self.mql_config.products_config[1],
			strategies=self.mql_config.strategies_config[0],
			forecast_weights=self.mql_config.strategies_config[1],
			vol_target=self.mql_config.vol_target,
			size_policy_class_=self.mql_config.size_policy_class_,
			estimator_params=self.mql_config.estimator_config_[1]
		)
		output = estimator_obj_.run()
		# add result writer process here
		return output


if __name__ == "__main__":
	# backtest
	# test_file_path = Path(__file__).parent / "mql/data/mql_backtest_template/backtest_example_query.sql"
	# fw opt
	test_file_path = Path(__file__).parent / "mql/data/mql_forecast_weights_optim/forecastweightsoptim_example_query.sql"
	# strat opt
	# asset select
	# alloc opt


	mql_proc = MqlProcess(mql_query_path=test_file_path)
	print(mql_proc.mql_config)

	result = mql_proc.run_process()
	print(result)

