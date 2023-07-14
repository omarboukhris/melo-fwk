from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.config.config_helper import ConfigBuilderHelper

class ProductFactory:
	"""
	Make this not static class
	init market loader from factory, use it in _get_product
	update usage in melo_config.py !
	"""
	def __init__(self, market_mgr):
		self.market = market_mgr
		self.plogger = GlobalLogger.build_composite_for(ProductFactory.__name__)

	def build_products(self, quant_query_dict: dict):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "ProductsDef")
		products_generator = ConfigBuilderHelper.strip_single(stripped_entry, "ProductsDefList")["ProductsGenerator"]
		time_period = [int(year) for year in stripped_entry.pop("timeperiod", [0, 0])]

		self.plogger.info("Loading Products")
		output_products = {}
		for prods in products_generator:
			products_type = ConfigBuilderHelper.strip_single(prods, "productType")
			products_name_list = ConfigBuilderHelper.parse_list(prods, "AlphanumList")
			for product_name in products_name_list:
				product = self._get_product(products_type, product_name)
				self.plogger.info(f"Loaded Product {product.keys()}")
				output_products.update(product)

		self.plogger.info(f"{len(output_products)} Products loaded")
		return output_products, time_period

	def _get_product(self, products_type: str, product_name: str) -> dict:
		"""
		TODO: add products leverage & size cap
			Rewrite this function to use the proper market from factories and apply lazy loading
			this should be done after rewriting market loaders and product factory registry for lazy loading
		"""
		assert products_type in QuantFlowFactory.products.keys(), \
			f"QuantFlowFactory: {products_type} key not in [{QuantFlowFactory.products.keys()}]"
		assert product_name in QuantFlowFactory.products[products_type], \
			f"QuantFlowFactory: {product_name} key not in [{QuantFlowFactory.products[products_type]}]"
		return {f"{products_type}.{product_name}": self.market.get(products_type, product_name)}

