
import glob
import random

import pandas as pd
import melo_fwk.datastreams.hloc_datastream as ds
from melo_fwk.market_data.product import Product

from pathlib import Path

products_block_size = {
	# Commodity
	"Brent Crude Oil": 1000,
	"Cocoa": 100,  #
	"Coffee": 100,  #
	"Copper": 10000,  #
	"Corn": 100,  #
	"Cotton": 100,  #
	"Crude Oil": 1000,  #
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
	"AUDUSD": 1e+5,
	"CADUSD": 1e+5,
	"CHFUSD": 1e+5,
	"EURCAD": 1e+5,
	"EURCHF": 1e+5,
	"EURGBP": 1e+5,
	"EURJPY": 1e+5,
	"EURUSD": 1e+5,
	"GBPUSD": 1e+5,
	"NZDUSD": 1e+5,
}

class MarketDataLoader:
	parent_folder = Path(Path(__file__).parent)
	mock_datastream_length = 1000

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
	def sample_products_pool(ratio: float):
		assert 0. < ratio <= 1., \
			f"(MarketDataLoader) Invalid sampling ratio provided {ratio} not in [0 ,1]"
		shuffled_pool, size = MarketDataLoader.shuffled_pool()
		return random.sample(shuffled_pool, int(size * ratio))

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
			product["name"],
			products_block_size[product["name"]],
			ds.HLOCDataStream(dataframe=input_df))

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
