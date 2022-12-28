
import glob
import json
import random

import pandas as pd
import melo_fwk.datastreams.hloc_datastream as ds
from melo_fwk.basket.product_basket import ProductBasket
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
		self.connect("market")
		output = self.db_connection.list_collection_names()
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
		self.connect("market")
		return [cname for cname in self.db_connection.list_collection_names() if cname[:2] == "fx"]

	def get_commodities(self):
		self.connect("market")
		return [cname for cname in self.db_connection.list_collection_names() if cname[:2] == "co"]

	def load_product_basket(self, product_basket_config: dict) -> ProductBasket:
		years = product_basket_config["years"]
		output = []
		for prod_name in product_basket_config["products"]:
			output.append(self.load_product(prod_name).get_years(years))

		return ProductBasket(output)


	def load_product(self, product: str) -> Product:
		self.connect("market")
		product_df = pd.DataFrame(self.select_request(product, verbose=False))
		del product_df["_id"]
		simple_prod_name = product.split(".")[1]
		return Product(
			name=product,
			block_size=self.product_config["products_block_size"][simple_prod_name],
			cap=self.product_config["products_cap_size"][simple_prod_name],
			datastream=ds.HLOCDataStream(dataframe=product_df))
