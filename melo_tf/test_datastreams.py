
from datastreams.backtest_data_loader import BacktestDataLoader
import tqdm

from typing import List

import unittest

class TestDataStreamsHelper:

	@staticmethod
	def test_mock_datastream(products: List[dict]):
		for product in tqdm.tqdm(products):
			_, pdstream = BacktestDataLoader.get_mock_datastream({})

			for tick in pdstream:

				TestDataStreams.quick_sanity_check(pdstream, product, tick)
				assert pdstream.get_diff_from_index(tick["Date"]) == 1

	@staticmethod
	def test_datastream(products: List[dict], years: List[str]):
		for product in tqdm.tqdm(products):
			_, pdstream = BacktestDataLoader.get_product_datastream(product)
			pdstream.parse_date_column()
			pdstream.with_daily_returns()
			# print(pdstream.get_data()[["Date", "Close", "Daily_diff"]])

			for y in years:
				yearly_pdstream = pdstream.get_data_by_year(y)
				if yearly_pdstream.get_data().empty:
					continue

				for tick in yearly_pdstream:
					TestDataStreams.quick_sanity_check(pdstream, product, tick)
					assert pdstream.get_diff_from_index(tick["Date"]) == y


	@staticmethod
	def quick_sanity_check(pdstream, product, tick):
		assert pdstream.get_current_date() == tick["Date"], \
			f"dates are different: {pdstream.get_current_date()} // {tick['Date']} in product {product['name']}"
		assert pdstream.get_open() == tick["Open"], \
			f"dates are different: {pdstream.get_open()} // {tick['Open']} in product {product['name']}"


class DataStreamUnitTests(unittest.TestCase):

	def test_mock_datastream(self):
		TestDataStreamsHelper.test_mock_datastream(
			BacktestDataLoader.get_sanitized_commodities()
		)

	def test_datastream_stocks(self):
		TestDataStreamsHelper.test_datastream(
			BacktestDataLoader.get_products("data/Stocks/*.csv"),
			[str(i) for i in range(2000, 2022)]
		)

	def test_datastream_commodities(self):
		TestDataStreamsHelper.test_datastream(
			BacktestDataLoader.get_sanitized_commodities(),
			[str(i) for i in range(2000, 2022)]
		)


if __name__ == "__main__":
	unittest.main()

