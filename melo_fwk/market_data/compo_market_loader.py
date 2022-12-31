import json
from pathlib import Path
from typing import List

from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.market_data.market_data_loader import MarketDataLoader
from melo_fwk.market_data.market_data_mongo_loader import MarketDataMongoLoader
from melo_fwk.market_data.product import Product
from melo_fwk.loggers.global_logger import GlobalLogger


class CompositeMarketLoader(BaseMarketLoader):

	def __init__(self, market_loaders: List[BaseMarketLoader]):
		super().__init__()
		self.market_loaders = market_loaders
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)

	@staticmethod
	def from_config(config_path: str):
		with open(config_path, "r") as fs:
			out = json.load(fs)
		market_loaders = [
			MarketDataMongoLoader(out["dburl"]),
			MarketDataLoader(Path(out["fallback_path"])),
		]
		if not out["mongo_first"]:
			market_loaders.reverse()
		return CompositeMarketLoader(market_loaders)

	@staticmethod
	def with_mongo_first(dburl: str, fallback_path: str):
		return CompositeMarketLoader(
			market_loaders=[
				MarketDataMongoLoader(dburl),
				MarketDataLoader(Path(fallback_path)),
			]
		)

	@staticmethod
	def with_mongo_second(dburl: str, fallback_path: str):
		return CompositeMarketLoader(
			market_loaders=[
				MarketDataLoader(Path(fallback_path)),
				MarketDataMongoLoader(dburl),
			]
		)

	def products_pool(self):
		# mongo can fail with ServerSelectionTimeoutError
		for market_loader in self.market_loaders:
			try:
				return market_loader.products_pool()
			except Exception as e:
				self.logger.warn(f"{type(market_loader).__name__} failed .products_pool() : {e}")

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
