
import pandas as pd
import tqdm

from melo_tf.rules.ewma_rule import EWMATradingRule
# from rules.sma_rule import SMATradingRule
from melo_tf.plots.plots import ForecastPlotter, HLOCPricePlotter
from melo_tf.datastreams import backtest_data_loader as bdl

import unittest

class TradingRuleUnitTests(unittest.TestCase):

	def test_trading_rule(self):
		products = bdl.BacktestDataLoader.get_products("melo_tf/data/CommodityData/*_sanitized.csv")
		for product in tqdm.tqdm(products):
			_, pds = bdl.BacktestDataLoader.get_product_datastream(product)
			pds.with_daily_returns()

			ewma_params = {
				"fast_span": 32,
				"slow_span": 128,
				"scale": 6,
				"cap": 20,
			}
			ewma = EWMATradingRule(**ewma_params)

			output_forcast = []
			for _ in pds:
				window = pds.get_window()
				if window is not None:
					output_forcast.append({
						"Forecast": ewma.forecast(window),
						"Date": pds.get_current_date(),
					})

			forcast_df = pd.DataFrame(output_forcast)
			acc_plt = ForecastPlotter(forcast_df, pds.get_data())
			acc_plt.save_png(f"data/residual/{product['name']}_plot.png")

			price_plt = HLOCPricePlotter(pds.get_data())
			price_plt.save_png(f"data/residual/test_trading_rule_{product['name']}_price_plot")


if __name__ == "__main__":
	unittest.main()
