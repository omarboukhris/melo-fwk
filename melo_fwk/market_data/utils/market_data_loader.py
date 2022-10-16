
import glob
import pandas as pd
import melo_fwk.market_data.utils.hloc_datastream as ds
from melo_fwk.market_data.product import Product

from pathlib import Path

class MarketDataLoader:
	parent_folder = Path(Path(__file__).parent)
	mock_datastream_length = 1000

	@staticmethod
	def get_sanitized_commodity_hloc_datastream(product: str):
		product_list = MarketDataLoader.get_products(f"assets/Commodity/{product}_sanitized.csv")
		assert len(product_list) == 1, \
			f"BacktestDataLoader.get_sanitized_commodity_hloc_datastream, product = {product_list}"

		return MarketDataLoader.get_product_datastream(product_list[0])

	@staticmethod
	def get_fx_hloc_datastream(product: str):
		product_list = MarketDataLoader.get_products(f"assets/Fx/{product}_1d_10y.csv")
		assert len(product_list) == 1, \
			f"BacktestDataLoader.get_fx_hloc_datastream, product = {product_list}"

		return MarketDataLoader.get_product_datastream(product_list[0])

	@staticmethod
	def get_product_datastream(product: dict) -> Product:
		input_df = pd.read_csv(product["datasource"])
		return Product(product["datasource"], ds.HLOCDataStream(input_df))

	@staticmethod
	def get_products(path: str):
		""" Globs historic data files and prepares them in a list
		of instruments to trade

		:param path: to glob files from
		:return: list of products with each product a key/value pair = {"name", "datasource"}
		"""
		btpath = str(MarketDataLoader.parent_folder.parent / path)
		product_path_list = glob.glob(btpath)
		output = []
		for path in product_path_list:
			product_name = path.split("/")[-1][:-4]
			output.append({"name": product_name, "datasource": path})
		return output

	@staticmethod
	def get_mock_datastream(_: dict):
		mock_dict = {
			"Date": [i for i in range(MarketDataLoader.mock_datastream_length)],
			"Close": [i for i in range(MarketDataLoader.mock_datastream_length)],
			"Open": [i for i in range(MarketDataLoader.mock_datastream_length)],
			"High": [i for i in range(MarketDataLoader.mock_datastream_length)],
			"Low": [i for i in range(MarketDataLoader.mock_datastream_length)],
		}
		mock_df = pd.DataFrame(mock_dict)
		return Product("mock_df", ds.HLOCDataStream(mock_df))

	@staticmethod
	def get_stocks():
		return MarketDataLoader.get_products("assets/Stocks/*.csv")

	@staticmethod
	def get_commodities():
		return MarketDataLoader.get_products("assets/Commodity/*.csv")

	@staticmethod
	def get_sanitized_commodities():
		return MarketDataLoader.get_products("assets/Commodity/*_sanitized.csv")
