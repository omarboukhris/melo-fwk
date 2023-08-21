
from pathlib import Path
from typing import List

import pandas as pd
import melo_fwk.datastreams.hloc_datastream as ds
from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.market_data.product import Product
from mutils.generic_config_loader import GenericConfigLoader


class MarketDataLoader(BaseMarketLoader):

	def __init__(self):
		super().__init__()
		param_map = GenericConfigLoader.get_node(MarketDataLoader.__name__, {})
		self.asset_path = Path(param_map["location"])
		self.glob_all = param_map["all"]

	def load_product_basket(self, product_basket_config: dict) -> ProductBasket:
		"""
		Rewrite this
			use product factory registry and .get()

		:param product_basket_config:
		:return:
		"""
		registry = pd.DataFrame(self._get_dataset_locations(self.glob_all))
		years = product_basket_config["years"]
		output = []
		for prod_name in product_basket_config["products"]:
			prod_dict = (registry[registry.name == prod_name]).to_dict("records")[0]
			output.append(self._load_product(prod_dict).get_years(years))

		return ProductBasket(output)

	def get_fx(self) -> List[Product]:
		return [self._load_product(p) for p in self._get_dataset_locations(self.glob_all.replace("**", "Fx"))]

	def get_commodities(self) -> List[Product]:
		return [self._load_product(p) for p in self._get_dataset_locations(self.glob_all.replace("**", "Commodities"))]

	def get(self, category: str, product: str, leverage: float = 1.0, size_cap: float = 50.) -> Product:
		product_list = self._get_dataset_locations(f"{category}/{product}.csv")
		assert len(product_list) == 1, \
			f"BacktestDataLoader.get({category}, {product}) Failed, product = {product_list}"
		return self._load_product(next(iter(product_list)), leverage, size_cap)

	def _load_product(self, product: dict, leverage: float = 1.0, size_cap: float = 50.) -> Product:
		input_df = pd.read_csv(product["datasource"])
		return Product(
			name=product["name"],
			block_size=leverage,
			cap=size_cap,
			datastream=ds.HLOCDataStream(dataframe=input_df))

	def _get_dataset_locations(self, path: str) -> List[dict]:
		""" Globs historic data files and prepares them in a list
		of instruments to trade

		:param path: to glob files from
		:return: list of products with each product a key/value pair = {"name", "datasource"}
		"""
		product_path_list = self.asset_path.glob(path)
		output = []
		for p_pr in product_path_list:
			p_path = str(p_pr)
			product_name = p_path.split("/")[-1][:-4]
			output.append({"name": product_name, "datasource": p_path})
		return output
