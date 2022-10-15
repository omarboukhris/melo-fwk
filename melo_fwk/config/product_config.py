
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.datastreams.index_builder import IndexBuilder
from melo_fwk.config.config_helper import ConfigBuilderHelper

class ProductConfigBuilder:
	@staticmethod
	def build_products(quant_query_dict: dict):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "ProductsDef")
		products_generator = ConfigBuilderHelper.strip_single(stripped_entry, "ProductsDefList")["ProductsGenerator"]
		instruments = ConfigBuilderHelper.strip_single(stripped_entry, "instrument")
		time_period = [int(year) for year in stripped_entry["timeperiod"]]

		output_products = {}
		for prods in products_generator:
			products_type = ConfigBuilderHelper.strip_single(prods, "productType")
			products_name_list = ConfigBuilderHelper.parse_list(prods, "ProductsList")
			for product_name in products_name_list:
				output_products.update(ProductConfigBuilder._get_product(products_type, product_name))

		# if idx build index otherwise trade singles
		if instruments == "idx":
			return IndexBuilder.build(output_products), time_period
		# else: trade singles
		return output_products, time_period

	@staticmethod
	def _get_product(products_type: str, product_name: str) -> dict:
		product_factory_name = f"{products_type}.{product_name}"
		assert product_factory_name in QuantFlowFactory.products.keys(), \
			f"QuantFlowFactory: {product_factory_name} product key not in [{QuantFlowFactory.products.keys()}]"
		return {product_factory_name: QuantFlowFactory.get_product(product_factory_name)}

