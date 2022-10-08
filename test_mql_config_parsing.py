
from mql.mql_parser import MqlParser

from melo_tf import quantfactory_registry
from melo_tf.melo_config import \
	ConfigBuilderHelper, \
	ProductConfigBuilder, \
	SizePolicyConfigBuilder

from pathlib import Path

if __name__ == "__main__":
	test_file_path = str(Path(__file__).parent / "mql/data/mql/backtest_example_query.sql")

	mql_parser = MqlParser()
	parsed_mql = mql_parser.parse_to_json(test_file_path)
	quant_query = ConfigBuilderHelper.strip_single(parsed_mql, "QuantQuery")

	print(quant_query)
	print(ProductConfigBuilder.build_products(quant_query))
	print(SizePolicyConfigBuilder.build_size_policy(quant_query))
	# Strategies
	# Estimator
