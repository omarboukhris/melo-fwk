
import glob
import random
from pathlib import Path
from typing import List

import pandas as pd
import melo_fwk.datastreams.hloc_datastream as ds
from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.db.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.db.market_data.product import Product


class MarketDataLoader(BaseMarketLoader):

	def __init__(self, asset_path: Path = BaseMarketLoader.parent_folder):
		super().__init__()
		self.asset_path = asset_path

	def load_product_basket(self, product_basket_config: dict) -> ProductBasket:
		registry = pd.DataFrame(self._get_dataset_locations("assets/*.csv"))
		years = product_basket_config["years"]
		output = []
		for prod_name in product_basket_config["products"]:
			prod_dict = dict(registry[registry.name == prod_name])
			output.append(self._load_product(prod_dict).get_years(years))

		return ProductBasket(output)

	def get_fx(self) -> List[Product]:
		return [self._load_product(p) for p in self._get_dataset_locations("assets/Fx/*.csv")]

	def get_commodities(self) -> List[Product]:
		return [self._load_product(p) for p in self._get_dataset_locations("assets/Commodity/*.csv")]

	def get_commodity_product(self, product: str) -> Product:
		product_list = self._get_dataset_locations(f"assets/Commodity/{product}.csv")
		assert len(product_list) == 1, \
			f"BacktestDataLoader.get_sanitized_commodity_hloc_datastream, product = {product_list}"

		return self._load_product(product_list[0])

	def get_fx_product(self, product: str) -> Product:
		product_list = self._get_dataset_locations(f"assets/Fx/{product}.csv")
		assert len(product_list) == 1, \
			f"BacktestDataLoader.get_fx_hloc_datastream, product = {product_list}"

		return self._load_product(product_list[0])

	def _load_product(self, product: dict) -> Product:
		input_df = pd.read_csv(product["datasource"])
		return Product(
			name=product["name"],
			block_size=self.product_config["products_block_size"][product["name"]],
			cap=self.product_config["products_cap_size"][product["name"]],
			datastream=ds.HLOCDataStream(dataframe=input_df))

	def _get_dataset_locations(self, path: str) -> List[dict]:
		""" Globs historic data files and prepares them in a list
		of instruments to trade

		:param path: to glob files from
		:return: list of products with each product a key/value pair = {"name", "datasource"}
		"""
		btpath = str(self.asset_path / path)
		product_path_list = glob.glob(btpath)
		output = []
		for path in product_path_list:
			product_name = path.split("/")[-1][:-4]
			output.append({"name": product_name, "datasource": path})
		return output
