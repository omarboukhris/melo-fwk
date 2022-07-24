
from datastreams.backtest_data_loader import BacktestDataLoader
import tqdm

from typing import List

class TestDataStreams:

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


if __name__ == "__main__":
	TestDataStreams.test_mock_datastream(
		BacktestDataLoader.get_sanitized_commodities()
	)

	TestDataStreams.test_datastream(
		BacktestDataLoader.get_products("data/Stocks/*.csv"),
		[str(i) for i in range(2000, 2022)]
	)

	TestDataStreams.test_datastream(
		BacktestDataLoader.get_sanitized_commodities(),
		[str(i) for i in range(2000, 2022)]
	)



