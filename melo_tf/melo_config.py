
from quantfactory_registry import quantflow_factory
from process.policies.vol_target_policy import VolTarget

class ConfigBuilderHelper:
	@staticmethod
	def strip(parsed_dict: dict, key: str):
		assert key in parsed_dict.keys(), f"Key [{key}] not in Dictionary keys [{parsed_dict.keys()}]"
		assert len(parsed_dict[key]) >= 1, f"Key [{key}] not in Dictionary keys [{parsed_dict.keys()}]"
		return parsed_dict[key]

	@staticmethod
	def strip_single(parsed_dict: dict, key: str):
		return ConfigBuilderHelper.strip(parsed_dict, key)[0]

	@staticmethod
	def parse_list(parsed_dict: dict, key: str):
		str_list = ConfigBuilderHelper.strip_single(parsed_dict, key)
		return [e.strip() for e in str_list.split(",")]

	@staticmethod
	def parse_num_list(parsed_dict: dict, key: str):
		str_list = ConfigBuilderHelper.strip_single(parsed_dict, key)
		return [float(e.strip()) for e in str_list.split(",")]

class SizePolicyConfigBuilder:
	@staticmethod
	def build_size_policy(quant_query_dict: dict):
		position_size_dict = ConfigBuilderHelper.strip_single(quant_query_dict, "PositionSizing")

		size_policy_factory_name = ConfigBuilderHelper.strip_single(position_size_dict, "SizePolicy")
		assert size_policy_factory_name in quantflow_factory.QuantFlowFactory.size_policies.keys(), \
			f"{size_policy_factory_name} key is not in [{quantflow_factory.QuantFlowFactory.size_policies.keys()}]"
		_SizePolicyClass = quantflow_factory.QuantFlowFactory.size_policies[size_policy_factory_name]

		vol_target_cfg = ConfigBuilderHelper.parse_num_list(position_size_dict, "VolTargetCouple")
		vol_target = VolTarget(*vol_target_cfg)
		return _SizePolicyClass(vol_target)


class ProductConfigBuilder:
	@staticmethod
	def build_products(quant_query_dict: dict):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "ProductsDef")
		products_generator = ConfigBuilderHelper.strip_single(stripped_entry, "ProductsDefList")["ProductsGenerator"]
		instruments = stripped_entry["instrument"]  # if idx build index otherwise trade singles

		output_products = []
		for prods in products_generator:
			products_type = ConfigBuilderHelper.strip_single(prods, "productType")
			products_name_list = ConfigBuilderHelper.parse_list(prods, "ProductsList")
			for product_name in products_name_list:
				output_products.append(ProductConfigBuilder._get_product(products_type, product_name))

		if instruments == "idx":
			# build index
			pass
		# else: trade singles
		return output_products

	@staticmethod
	def _get_product(products_type: str, product_name: str) -> tuple:
		product_factory_name = f"{products_type}.{product_name}"
		assert product_factory_name in quantflow_factory.QuantFlowFactory.products.keys(), \
			f"QuantFlowFactory: {product_factory_name} product key not in [{quantflow_factory.QuantFlowFactory.products.keys()}]"
		return quantflow_factory.QuantFlowFactory.products[product_factory_name]


"""
MeloQL - Interpreter Spec: Chronological Model Backtesting
Cov Heat Map : 
	N Products in Q Asset Class in 1 Portfolio
	1 Mql query file for each asset class
	output :
		Cov Heat Map
		Clustering
		folders with template startoptim/vol queries
	Notes: make structured query folder generator from heatmap/clustering (optional) result
Strat/VolTarget Estimators :
	M < Nq Products in Asset Class Q -> (K Strategies, VolTarget)
	1 Mql query file by trading subsystem
	output :
		Optim Strat Config. location: tbd
		Forecast Weights + Div Mult. location: tbd
		VolTarget. location: tbd
	Notes: make loader/writer for these estimators, register in factory
Backtest Estimator :
	M < N Correllated Products -> (K Strategies, VolTarget)
	1 Mql query file by trading subsystem
	output : 
		Backtest Report
Allocation Optim :
	N Products in Q Asset Class in 1 Portfolio
	1 Mql query file for whole portfolio
	output :
		Allocation Weights Optim. location: tbd
"""
if __name__ == "__main__":
	# this should get out of folder to parent
	# mql should be moved out too
	# mql query config parsing example
	from mql.mql_parser import MqlParser
	from pathlib import Path

	test_file_path = str(Path(__file__).parent / "mql/data/mql/backtest_example_query.sql")

	mql_parser = MqlParser()
	parsed_mql = mql_parser.parse_to_json(test_file_path)
	quant_query = ConfigBuilderHelper.strip_single(parsed_mql, "QuantQuery")

	print(quant_query)
	print(ProductConfigBuilder.build_products(quant_query))
	print(SizePolicyConfigBuilder.build_size_policy(quant_query))
	# Strategies
	# Estimator
