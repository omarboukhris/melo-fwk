import pandas as pd
import melo_fwk.datastreams.hloc_datastream as ds
from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from mutils.generic_config_loader import GenericConfigLoader
from mutils.mongo_db_mgr import MongodbManager
from melo_fwk.market_data.product import Product


class MarketDataMongoLoader(BaseMarketLoader):

	def __init__(self):
		super().__init__()
		config = GenericConfigLoader.get_node(MarketDataMongoLoader.__name__, {})
		dburl = config["dburl"]
		self.mongo_mgr = MongodbManager(dburl)

	def load_product_basket(self, product_basket_config: dict) -> ProductBasket:
		years = product_basket_config["years"]
		output = []
		for prod_name in product_basket_config["products"]:
			output.append(self._load_product(prod_name).get_years(years))

		return ProductBasket(output)

	def products_pool(self):
		self.mongo_mgr.connect("market")
		products = self.mongo_mgr.db_connection.list_collection_names()
		return [self._load_product(p) for p in products]

	def get(self, category: str, product: str, leverage, size_cap):
		self.mongo_mgr.connect("market")
		return [
			self._load_product(cname)
			for cname in self.mongo_mgr.db_connection.list_collection_names()
			if f"{category}." in cname
		]

	def get_fx(self):
		self.mongo_mgr.connect("market")
		return [
			self._load_product(cname)
			for cname in self.mongo_mgr.db_connection.list_collection_names()
			if cname[:2] == "fx"
		]

	def get_commodities(self):
		self.mongo_mgr.connect("market")
		return [
			self._load_product(cname)
			for cname in self.mongo_mgr.db_connection.list_collection_names()
			if cname[:2] == "co"
		]

	def _load_product(self, product: str) -> Product:
		""" this should be rewritten once cap size, block size is written in config spec
		"""
		self.mongo_mgr.connect("market")
		product_df = pd.DataFrame(self.mongo_mgr.select_request(product, verbose=False))
		del product_df["_id"]
		simple_prod_name = product.split(".")[1]
		return Product(
			name=product,
			block_size=self.product_config["products_block_size"][simple_prod_name],
			cap=self.product_config["products_cap_size"][simple_prod_name],
			datastream=ds.HLOCDataStream(dataframe=product_df))
