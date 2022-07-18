
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
	def get_products(path: str):
		product_path_list = glob.glob(path)
		output = []
		for path in product_path_list:
			product_name = path.split("/")[-1][:-4]
			output.append({"name": product_name, "datasource": path})
		return output

	@staticmethod
	def get_product_datastream(product: dict):
		input_df = pd.read_csv(product["datasource"])
		return input_df, ds.PandasDataStream(product["name"], input_df)

	@staticmethod
	def get_mock_datastream(_: dict):
		mock_dict = {
			"Date": [i for i in range(BacktestDataLoader.mock_datastream_length)],
			"Close": [i for i in range(BacktestDataLoader.mock_datastream_length)]
		}
		mock_df = pd.DataFrame(mock_dict)
		return mock_df, ds.PandasDataStream("mock", mock_df)
