
from mql.mql_parser import MqlParser

from melo_fwk import quantfactory_registry
from melo_fwk.melo_config import \
	ConfigBuilderHelper, \
	ProductConfigBuilder, \
	StrategyConfigBuilder, \
	StratConfigRegistry, \
	SizePolicyConfigBuilder

from pathlib import Path

if __name__ == "__main__":
	test_file_path = str(Path(__file__).parent / "mql/data/mql/backtest_example_query.sql")
	strat_config_file_path = str(Path(__file__).parent / "mql/data/mql_forecast_weights_optim")

	quantfactory_registry.register_all()

	mql_parser = MqlParser()
	parsed_mql = mql_parser.parse_to_json(test_file_path)
	quant_query = ConfigBuilderHelper.strip_single(parsed_mql, "QuantQuery")

	strat_config_registry = StratConfigRegistry(strat_config_file_path)
	print(quant_query)
	print(ProductConfigBuilder.build_products(quant_query))
	print(SizePolicyConfigBuilder.build_size_policy(quant_query))
	print(strat_config_registry)
	print(StrategyConfigBuilder.build_strategy(quant_query, strat_config_registry))
	# Estimator
