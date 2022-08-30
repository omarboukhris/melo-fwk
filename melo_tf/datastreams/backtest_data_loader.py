
import glob
import pandas as pd
import datastreams.datastream as ds

class BacktestDataLoader:

	mock_datastream_length = 1000

	@staticmethod
	def get_stocks():
		return BacktestDataLoader.get_products("data/Stocks/*.csv")

	@staticmethod
	def get_commodities():
		return BacktestDataLoader.get_products("data/CommodityData/*.csv")

	@staticmethod
	def get_sanitized_commodities():
		return BacktestDataLoader.get_products("data/CommodityData/*_sanitized.csv")

	@staticmethod
	def get_sanitized_commodity_hloc_datastream(product: str):
		product_list = BacktestDataLoader.get_products(f"data/CommodityData/{product}_sanitized.csv")
		assert len(product_list) == 1, \
			f"BacktestDataLoader.get_sanitized_commodity_hloc_datastream, product = {product_list}"

		return BacktestDataLoader.get_product_datastream(product_list[0])

	@staticmethod
	def get_products(path: str):
		""" Globs historic data files and prepares them in a list
		of instruments to trade

		:param path: to glob files from
		:return: list of products with each product a key/value pair = {"name", "datasource"}
		"""
		product_path_list = glob.glob(path)
		output = []
		for path in product_path_list:
			product_name = path.split("/")[-1][:-4]
			output.append({"name": product_name, "datasource": path})
		return output

	@staticmethod
	def get_product_datastream(product: dict):
		input_df = pd.read_csv(product["datasource"])
		return input_df, ds.HLOCDataStream(input_df)

	@staticmethod
	def get_mock_datastream(_: dict):
		mock_dict = {
			"Date": [i for i in range(BacktestDataLoader.mock_datastream_length)],
			"Close": [i for i in range(BacktestDataLoader.mock_datastream_length)],
			"Open": [i for i in range(BacktestDataLoader.mock_datastream_length)],
			"High": [i for i in range(BacktestDataLoader.mock_datastream_length)],
			"Low": [i for i in range(BacktestDataLoader.mock_datastream_length)],
		}
		mock_df = pd.DataFrame(mock_dict)
		return mock_df, ds.HLOCDataStream(mock_df)
