
import glob
import pandas as pd
import melo_fwk.datastreams.hloc_datastream as ds
from melo_fwk.market_data.utils.product import Product

from pathlib import Path

class MarketDataLoader:
	parent_folder = Path(Path(__file__).parent)
	mock_datastream_length = 1000

	@staticmethod
	def get_fx():
		return MarketDataLoader.get_dataset_locations("assets/Fx/*.csv")

	@staticmethod
	def get_commodities():
		return MarketDataLoader.get_dataset_locations("assets/Commodity/*.csv")

	@staticmethod
	def get_commodity_hloc_datastream(product: str):
		product_list = MarketDataLoader.get_dataset_locations(f"assets/Commodity/{product}.csv")
		assert len(product_list) == 1, \
			f"BacktestDataLoader.get_sanitized_commodity_hloc_datastream, product = {product_list}"

		return MarketDataLoader.load_datastream(product_list[0])

	@staticmethod
	def get_fx_hloc_datastream(product: str):
		product_list = MarketDataLoader.get_dataset_locations(f"assets/Fx/{product}.csv")
		assert len(product_list) == 1, \
			f"BacktestDataLoader.get_fx_hloc_datastream, product = {product_list}"

		return MarketDataLoader.load_datastream(product_list[0])

	@staticmethod
	def load_datastream(product: dict) -> Product:
		input_df = pd.read_csv(product["datasource"])
		return Product(product["name"], ds.HLOCDataStream(dataframe=input_df))

	@staticmethod
	def get_dataset_locations(path: str):
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
