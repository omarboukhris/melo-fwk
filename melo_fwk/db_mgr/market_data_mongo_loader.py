
import glob
import json
import random

import pandas as pd
import melo_fwk.datastreams.hloc_datastream as ds
from melo_fwk.db_mgr.mongo_db_mgr import MongodbManager
from melo_fwk.market_data.product import Product

from pathlib import Path

class MarketDataMongoLoader(MongodbManager):
	parent_folder = Path(Path(__file__).parent)

	def __init__(self, dburl: str = "mongodb://localhost:27017/"):
		super().__init__(dburl)
		with open(MarketDataMongoLoader.parent_folder / "config/products_config.json") as fp:
			self.product_config = json.load(fp)

	def products_pool(self):
		self.connect("Commodity")
		output = self.db_connection.list_collection_names()
		self.connect("Fx")
		output += self.db_connection.list_collection_names()
		return output

	def shuffled_pool(self):
		pool = self.products_pool()
		random.shuffle(pool)
		return pool, len(pool)

	def sample_products(self, n_products: int):
		shuffled_pool, size = self.shuffled_pool()
		assert 0. < n_products < size, \
			f"(MarketDataLoader) Invalid sampling ratio provided {n_products} not in [0 ,{size}]"
		return random.sample(shuffled_pool, n_products)

	def sample_products_alpha(self, alpha: float):
		assert 0. < alpha <= 1., \
			f"(MarketDataLoader) Invalid sampling ratio provided {alpha} not in [0 ,1]"
		shuffled_pool, size = self.shuffled_pool()
		return random.sample(shuffled_pool, int(size * alpha))

	def get_fx(self):
		self.connect("Fx")
		return self.db_connection.list_collection_names()

	def get_commodities(self):
		self.connect("Commodity")
		return self.db_connection.list_collection_names()

	def load_fx(self, product: str):
		return self.load_product("Fx", product)

	def load_commomdity(self, product: str):
		return self.load_product("Commodity", product)

	def load_product(self, dbname: str, product: str):
		self.connect(dbname)
		product_df = pd.DataFrame(self.select_request(product, verbose=False))
		del product_df["_id"]
		return Product(
			name=product,
			block_size=self.product_config["products_block_size"][product],
			cap=self.product_config["products_cap_size"][product],
			datastream=ds.HLOCDataStream(dataframe=product_df))
