
from datastreams.backtest_data_loader import BacktestDataLoader
import tqdm

from typing import List

class TestDataStreams:

	@staticmethod
	def test_datastream(products: List[dict]):
		for product in tqdm.tqdm(products):
			_, pdstream = BacktestDataLoader.get_product_datastream(product)

			for tick in pdstream:

				TestDataStreams.quick_sanity_check(pdstream, product, tick)
				# print(tick["Date"], "//", tick["Close"], pdstream.get_diff_from_index(tick["Date"]))

	@staticmethod
	def quick_sanity_check(pdstream, product, tick):
		assert pdstream.get_current_date() == tick["Date"], \
			f"dates are different: {pdstream.get_current_date()} // {tick['Date']} in product {product['name']}"
		assert pdstream.get_open() == tick["Open"], \
			f"dates are different: {pdstream.get_open()} // {tick['Open']} in product {product['name']}"


if __name__ == "__main__":
	TestDataStreams.test_datastream(
		BacktestDataLoader.get_sanitized_commodities()
	)



