from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.config.config_helper import ConfigBuilderHelper

class ProductConfigBuilder:
	@staticmethod
	def build_products(quant_query_dict: dict):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "ProductsDef")
		products_generator = ConfigBuilderHelper.strip_single(stripped_entry, "ProductsDefList")["ProductsGenerator"]
		time_period = [int(year) for year in stripped_entry.pop("timeperiod", [0, 0])]

		plogger = GlobalLogger.build_composite_for("ProductConfigBuilder")
		plogger.info("Loading Products")
		output_products = {}
		for prods in products_generator:
			products_type = ConfigBuilderHelper.strip_single(prods, "productType")
			products_name_list = ConfigBuilderHelper.parse_list(prods, "AlphanumList")
			for product_name in products_name_list:
				product = ProductConfigBuilder._get_product(products_type, product_name)
				plogger.info(f"Loaded Product {product.keys()}")
				output_products.update(product)

		plogger.info(f"{len(output_products)} Products loaded")
		return output_products, time_period

	@staticmethod
	def _get_product(products_type: str, product_name: str) -> dict:
		""" add option to load from market ??"""
		product_factory_name = f"{products_type}.{product_name}"
		assert product_factory_name in QuantFlowFactory.products.keys(), \
			GlobalLogger.build_composite_for("ProductConfigBuilder").error(
				f"QuantFlowFactory: {product_factory_name} product key not in [{QuantFlowFactory.products.keys()}]")
		return {product_factory_name: QuantFlowFactory.get_product(product_factory_name)}

