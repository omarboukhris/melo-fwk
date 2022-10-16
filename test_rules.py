
import pandas as pd
import tqdm

from melo_fwk.rules.ewma import EWMATradingRule
# from rules.sma_rule import SMATradingRule
from melo_fwk.plots.plots import ForecastPlotter, HLOCPricePlotter
from melo_fwk.datastreams import backtest_data_loader as bdl

import unittest

class TradingRuleUnitTests(unittest.TestCase):

	def test_vectorized_trading_rule(self):
		products = bdl.BacktestDataLoader.get_products("assets/CommodityData/*_sanitized.csv")
		for product in tqdm.tqdm(products):
			product_hloc = bdl.BacktestDataLoader.get_product_datastream(product)
			product_hloc.datastream.with_daily_returns()

			ewma_params = {
				"fast_span": 32,
				"slow_span": 128,
				"scale": 6,
				"cap": 20,
			}
			ewma = EWMATradingRule(**ewma_params)

			f_dict = {
				"Date": product_hloc.datastream.get_data()["Date"],
				"Forecast": ewma.forecast_vect_cap(product_hloc.datastream.get_data()),
			}
			forecast_df = pd.DataFrame(f_dict)

			acc_plt = ForecastPlotter(forecast_df, product_hloc.datastream.get_data())
			acc_plt.save_png(f"data/residual/{product['name']}_plot_vect.png")


	def test_trading_rule(self):
		products = bdl.BacktestDataLoader.get_products("assets/CommodityData/*_sanitized.csv")
		for product in tqdm.tqdm(products[:1]):
			product_hloc = bdl.BacktestDataLoader.get_product_datastream(product)
			product_hloc.datastream.with_daily_returns()

			ewma_params = {
				"fast_span": 32,
				"slow_span": 128,
				"scale": 6,
				"cap": 20,
			}
			ewma = EWMATradingRule(**ewma_params)

			output_forcast = []
			for _ in product_hloc.datastream:
				window = product_hloc.datastream.get_window()
				if window is not None:
					output_forcast.append({
						"Forecast": ewma.forecast(window),
						"Date": product_hloc.datastream.get_current_date(),
					})

			forcast_df = pd.DataFrame(output_forcast)
			acc_plt = ForecastPlotter(forcast_df, product_hloc.datastream.get_data())
			acc_plt.save_png(f"data/residual/{product['name']}_plot.png")

			price_plt = HLOCPricePlotter(product_hloc.datastream.get_data())
			price_plt.save_png(f"data/residual/test_trading_rule_{product['name']}_price_plot")


if __name__ == "__main__":
	unittest.main()
