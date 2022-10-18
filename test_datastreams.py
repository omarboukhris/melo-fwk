
from melo_fwk.market_data.utils.market_data_loader import MarketDataLoader
from melo_fwk.market_data.utils.hloc_datastream import HLOCDataStream

import tqdm
import pandas as pd

from typing import List

import unittest

class TestDataStreamsHelper:

	@staticmethod
	def test_datastream(products: List[dict], years: List[str]):
		for product in tqdm.tqdm(products):
			loaded_prod = MarketDataLoader.load_datastream(product)

			for y in years:
				yearly_pdstream = loaded_prod.datastream.get_data_by_year(y)
				if yearly_pdstream.get_data().empty:
					continue

				for tick in yearly_pdstream:
					TestDataStreamsHelper.quick_sanity_check(loaded_prod.datastream, product, tick)
					assert loaded_prod.datastream.get_diff_from_index(tick["Date"]) == y


	@staticmethod
	def quick_sanity_check(pdstream, product, tick):
		assert pdstream.get_current_date() == tick["Date"], \
			f"dates are different: {pdstream.get_current_date()} // {tick['Date']} in product {product['name']}"
		assert pdstream.get_current_open() == tick["Open"], \
			f"dates are different: {pdstream.get_open()} // {tick['Open']} in product {product['name']}"


class DataStreamUnitTests(unittest.TestCase):

	def test_datastream(self):
		def process_tick(_):
			pass

		pdstream = HLOCDataStream(
			dataframe=pd.read_csv("melo_fwk/market_data/assets/Commodity/Cocoa.csv"))

		for tick in pdstream:
			process_tick(tick)

	def test_datastream_stocks(self):
		TestDataStreamsHelper.test_datastream(
			MarketDataLoader.get_dataset_locations("data/Stocks/*.csv"),
			[str(i) for i in range(2000, 2022)]
		)

	def test_datastream_commodities(self):
		TestDataStreamsHelper.test_datastream(
			MarketDataLoader.get_commodities(),
			[str(i) for i in range(2000, 2022)]
		)


if __name__ == "__main__":
	unittest.main()

