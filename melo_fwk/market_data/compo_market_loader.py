from typing import List

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.market_data.product import Product
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.utils.quantflow_factory import QuantFlowFactory


class CompositeMarketLoader(BaseMarketLoader):

	def __init__(self, market_loaders: List[BaseMarketLoader]):
		super().__init__()
		self.market_loaders = market_loaders
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)

	@staticmethod
	def from_config(market_config: List[str]):
		market_loaders = [QuantFlowFactory.get_market(market) for market in market_config]
		return CompositeMarketLoader(market_loaders)

	def load_product_basket(self, product_basket_config: dict) -> ProductBasket:
		# mongo can fail with ServerSelectionTimeoutError
		for market_loader in self.market_loaders:
			try:
				return market_loader.load_product_basket(product_basket_config)
			except Exception as e:
				self.logger.warn(f"{type(market_loader).__name__} failed .load_product_basket() : {e}")

		raise Exception("(CompositeMarketLoader) All alternatives failed")

	def products_pool(self):
		# mongo can fail with ServerSelectionTimeoutError
		for market_loader in self.market_loaders:
			try:
				return market_loader.products_pool()
			except Exception as e:
				self.logger.warn(f"{type(market_loader).__name__} failed .products_pool() : {e}")

		raise Exception("(CompositeMarketLoader) All alternatives failed")

	def get(self, category: str, product: str, leverage: float = 1.0, size_cap: float = 50.) -> Product:
		for market_loader in self.market_loaders:
			try:
				return market_loader.get(category, product, leverage, size_cap)
			except Exception as e:
				self.logger.warn(f"{type(market_loader).__name__} failed .load_product_basket() : {e}")

		raise Exception("(CompositeMarketLoader) All alternatives failed")

	def get_fx(self):
		for market_loader in self.market_loaders:
			try:
				return market_loader.get_fx()
			except Exception as e:
				self.logger.warn(f"{type(market_loader).__name__} failed .get_fx() : {e}")
		raise Exception("(CompositeMarketLoader) All alternatives failed")

	def get_commodities(self):
		for market_loader in self.market_loaders:
			try:
				return market_loader.get_commodities()
			except Exception as e:
				self.logger.warn(f"{type(market_loader).__name__} failed .get_commodities() : {e}")
		raise Exception("(CompositeMarketLoader) All alternatives failed")

	def _load_product(self, product: str) -> Product:
		for market_loader in self.market_loaders:
			try:
				return market_loader._load_product(product)
			except Exception as e:
				self.logger.warn(f"{type(market_loader).__name__} failed .load_product({product}) : {e}")
		raise Exception("(CompositeMarketLoader) All alternatives failed")
