from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.quantflow_factory import QuantFlowFactory
from mql.mconfig.mql_dict import MqlDict

class ProductFactory:
	"""
	Make this not static class
	init market loader from factory, use it in _get_product
	update usage in melo_config.py !
	"""
	def __init__(self, market_mgr):
		self.market = market_mgr
		self.plogger = GlobalLogger.build_composite_for(ProductFactory.__name__)

	def build_product_basket(self, mql_dict: MqlDict):
		raise NotImplementedError

	def build_products(self, mql_dict: MqlDict):
		prod_mql_dict = mql_dict.get_node("ProductsDef")
		products_generator = prod_mql_dict.get_node("ProductsDefList")["ProductsGenerator"]
		time_period = [int(x) for x in prod_mql_dict.get("timeperiod", [0, 0])]

		self.plogger.info("Loading Products")
		output_products = {}
		for prods in products_generator:
			prods_mql_dict = MqlDict(prods)
			products_type = prods_mql_dict.get_node("productType")
			products_name_list = prods_mql_dict.parse_list("AlphanumList")
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

