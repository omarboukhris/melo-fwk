
import pandas as pd
import tqdm

from melo_fwk.strategies import (
	EWMAStrategy,
	# SMAStrategy
)
from melo_fwk.plots.plots import ForecastPlotter, HLOCPricePlotter
from melo_fwk.market_data import market_data_loader as bdl

import unittest

class TradingRuleUnitTests(unittest.TestCase):

	def test_trading_rule(self):
		products = bdl.MarketDataLoader.get_commodities()
		for product in tqdm.tqdm(products):
			product_hloc = bdl.MarketDataLoader.load_datastream(product)

			ewma_params = {
				"fast_span": 32,
				"slow_span": 128,
			}
			ewma = EWMAStrategy(**ewma_params)

			forcast_df = pd.DataFrame({
				"Date": product_hloc.datastream.get_date_series(),
				"Forecast": ewma.forecast_vect_cap(
					product_hloc.datastream.get_close_series())
			})
			acc_plt = ForecastPlotter(forcast_df, product_hloc.datastream.get_dataframe())
			acc_plt.save_png(f"data/residual/{product['name']}_plot.png")

			price_plt = HLOCPricePlotter(product_hloc.datastream.get_dataframe())
			price_plt.save_png(f"data/residual/test_trading_rule_{product['name']}_price_plot")


if __name__ == "__main__":
	unittest.main()
