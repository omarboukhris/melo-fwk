
from mql.mql_parser import MqlParser
from quantfactory_registry import *


class MeloConfigBuilder:

	@staticmethod
	def build_products(quant_query_dict: dict):
		stripped_entry = MeloConfigBuilder.strip_single(quant_query_dict, "ProductsDef")
		products_generator = MeloConfigBuilder.strip_single(stripped_entry, "ProductsDefList")["ProductsGenerator"]
		instruments = stripped_entry["instrument"]  # if idx build index otherwise trade singles

		output_products = []
		for prods in products_generator:
			products_type = MeloConfigBuilder.strip_single(prods, "productType")
			products_name_list = MeloConfigBuilder.parse_list(prods, "ProductsList")
			for product_name in products_name_list:
				output_products.append(ProductConfigBuilder.get_product(products_type, product_name))

		if instruments == "idx":
			# build index
			pass
		# else: trade singles
		return output_products

	@staticmethod
	def strip(parsed_dict: dict, key: str):
		assert key in parsed_dict.keys(), f"Key [{key}] not in Dictionary keys [{parsed_dict.keys()}]"
		assert len(parsed_dict[key]) >= 1, f"Key [{key}] not in Dictionary keys [{parsed_dict.keys()}]"
		return parsed_dict[key]

	@staticmethod
	def strip_single(parsed_dict: dict, key: str):
		return MeloConfigBuilder.strip(parsed_dict, key)[0]

	@staticmethod
	def parse_list(parsed_dict: dict, key: str):
		str_list = MeloConfigBuilder.strip_single(parsed_dict, key)
		return [e.strip() for e in str_list.split(",")]


class ProductConfigBuilder:

	@staticmethod
	def get_product(products_type: str, product_name: str) -> tuple:
		product_factory_name = f"{products_type}.{product_name}"
		assert product_factory_name in quantflow_factory.QuantFlowFactory.products.keys(), \
			f"QuantFlowFactory: {product_factory_name} product key not in [{quantflow_factory.QuantFlowFactory.products.keys()}]"
		return quantflow_factory.QuantFlowFactory.products[product_factory_name]



if __name__ == "__main__":
	from pathlib import Path

	test_file_path = str(
		Path(__file__).parent /
		"mql/data/mql/backtest_example_query.sql"
	)

	mql_parser = MqlParser()
	parsed_mql = mql_parser.parse_to_json(test_file_path)
	quant_query = MeloConfigBuilder.strip_single(parsed_mql, "QuantQuery")
	print(MeloConfigBuilder.build_products(quant_query))
