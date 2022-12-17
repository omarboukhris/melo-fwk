
import glob
import random

import pandas as pd
import melo_fwk.datastreams.hloc_datastream as ds
from melo_fwk.market_data.product import Product

from pathlib import Path

products_block_size = {
	# Commodity
	"Brent Crude Oil": 100,
	"Cocoa": 100,  #
	"Coffee": 100,  #
	"Copper": 100,  #
	"Corn": 100,  #
	"Cotton": 100,  #
	"Crude Oil": 100,  #
	"Feeder Cattle": 100,  #
	"Gold": 100,  #
	"Lean Hogs": 100,  #
	"Live Cattle": 100,  #
	"Lumber": 100,  #
	"Natural Gas": 100,  #
	"Oat": 100,  #
	"Palladium": 100,  #
	"Platinum": 100,  #
	"RBOB Gasoline": 100,  #
	"Silver": 100,  #
	"Soybean": 100,  #
	"Soybean Meal": 100,  #
	"Soybean Oil": 100,  #
	"Sugar": 100,  #
	"Wheat": 100,  #

	# Fx
	"AUDUSD": int(1e+5),
	"CADUSD": int(1e+5),
	"CHFUSD": int(1e+5),
	"EURCAD": int(1e+5),
	"EURCHF": int(1e+5),
	"EURGBP": int(1e+5),
	"EURJPY": int(1e+5),
	"EURUSD": int(1e+5),
	"GBPUSD": int(1e+5),
	"NZDUSD": int(1e+5),
}

products_cap_size = {
	# Commodity
	"Brent Crude Oil": 100,
	"Cocoa": 100,  #
	"Coffee": 100,  #
	"Copper": 100,  #
	"Corn": 100,  #
	"Cotton": 100,  #
	"Crude Oil": 100,  #
	"Feeder Cattle": 100,  #
	"Gold": 100,  #
	"Lean Hogs": 100,  #
	"Live Cattle": 100,  #
	"Lumber": 100,  #
	"Natural Gas": 100,  #
	"Oat": 100,  #
	"Palladium": 100,  #
	"Platinum": 100,  #
	"RBOB Gasoline": 100,  #
	"Silver": 100,  #
	"Soybean": 100,  #
	"Soybean Meal": 100,  #
	"Soybean Oil": 100,  #
	"Sugar": 100,  #
	"Wheat": 100,  #

	# Fx
	"AUDUSD": 100,
	"CADUSD": 100,
	"CHFUSD": 100,
	"EURCAD": 100,
	"EURCHF": 100,
	"EURGBP": 100,
	"EURJPY": 100,
	"EURUSD": 100,
	"GBPUSD": 100,
	"NZDUSD": 100,
}

class MarketDataLoader:
	parent_folder = Path(Path(__file__).parent)

	@staticmethod
	def products_pool():
		products_loc = MarketDataLoader.get_commodities() + MarketDataLoader.get_fx()
		products = [MarketDataLoader.load_datastream(prod) for prod in products_loc]
		return products

	@staticmethod
	def shuffled_pool():
		pool = MarketDataLoader.products_pool()
		random.shuffle(pool)
		return pool, len(pool)

	@staticmethod
	def sample_products(n_products: int):
		shuffled_pool, size = MarketDataLoader.shuffled_pool()
		assert 0. < n_products < size, \
			f"(MarketDataLoader) Invalid sampling ratio provided {n_products} not in [0 ,{size}]"
		return random.sample(shuffled_pool, n_products)

	@staticmethod
	def sample_products_alpha(alpha: float):
		assert 0. < alpha <= 1., \
			f"(MarketDataLoader) Invalid sampling ratio provided {alpha} not in [0 ,1]"
		shuffled_pool, size = MarketDataLoader.shuffled_pool()
		return random.sample(shuffled_pool, int(size * alpha))

	@staticmethod
	def get_fx():
		return MarketDataLoader._get_dataset_locations("assets/Fx/*.csv")

	@staticmethod
	def get_commodities():
		return MarketDataLoader._get_dataset_locations("assets/Commodity/*.csv")

	@staticmethod
	def get_commodity_hloc_datastream(product: str):
		product_list = MarketDataLoader._get_dataset_locations(f"assets/Commodity/{product}.csv")
		assert len(product_list) == 1, \
			f"BacktestDataLoader.get_sanitized_commodity_hloc_datastream, product = {product_list}"

		return MarketDataLoader.load_datastream(product_list[0])

	@staticmethod
	def get_fx_hloc_datastream(product: str):
		product_list = MarketDataLoader._get_dataset_locations(f"assets/Fx/{product}.csv")
		assert len(product_list) == 1, \
			f"BacktestDataLoader.get_fx_hloc_datastream, product = {product_list}"

		return MarketDataLoader.load_datastream(product_list[0])

	@staticmethod
	def load_datastream(product: dict) -> Product:
		input_df = pd.read_csv(product["datasource"])
		return Product(
			name=product["name"],
			block_size=products_block_size[product["name"]],
			cap=products_cap_size[product["name"]],
			datastream=ds.HLOCDataStream(dataframe=input_df))

	@staticmethod
	def _get_dataset_locations(path: str):
		""" Globs historic data files and prepares them in a list
		of instruments to trade

		:param path: to glob files from
		:return: list of products with each product a key/value pair = {"name", "datasource"}
		"""
		btpath = str(MarketDataLoader.parent_folder / path)
		product_path_list = glob.glob(btpath)
		output = []
		for path in product_path_list:
			product_name = path.split("/")[-1][:-4]
			output.append({"name": product_name, "datasource": path})
		return output
