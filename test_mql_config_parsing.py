
from mql.mql_parser import MqlParser

from melo_fwk import quantfactory_registry
from melo_fwk.melo_config import \
	ConfigBuilderHelper, \
	ProductConfigBuilder, \
	StrategyConfigBuilder, \
	StratConfigRegistry, \
	SizePolicyConfigBuilder, \
	EstimatorConfigBuilder

from pathlib import Path

if __name__ == "__main__":
	test_file_path = str(Path(__file__).parent / "mql/data/mql/backtest_example_query.sql")
	strat_config_file_path = str(Path(__file__).parent / "mql/data/mql_forecast_weights_optim")

	quantfactory_registry.register_all()

	mql_parser = MqlParser()
	parsed_mql = mql_parser.parse_to_json(test_file_path)
	quant_query = ConfigBuilderHelper.strip_single(parsed_mql, "QuantQuery")

	products_config = ProductConfigBuilder.build_products(quant_query)
	size_policy_class_ = SizePolicyConfigBuilder.build_size_policy(quant_query)
	strat_config_registry = StratConfigRegistry(strat_config_file_path)
	strategies_config = StrategyConfigBuilder.build_strategy(quant_query, strat_config_registry)
	estimator_config_ = EstimatorConfigBuilder.build_estimator(quant_query)

	print(quant_query)
	print(products_config)
	print(size_policy_class_)
	print(strat_config_registry)
	print(strategies_config)
	print(estimator_config_)

	# run workflow
	estimator_obj_ = estimator_config_[0](
		balance=60000,
		products=products_config[0],
		time_period=products_config[1],
		strategies=strategies_config[0],
		forecast_weights=strategies_config[1],
		size_policy_class_=size_policy_class_,
		estimator_params=estimator_config_[1]
	)
	output = estimator_obj_.run()
	print(output)
