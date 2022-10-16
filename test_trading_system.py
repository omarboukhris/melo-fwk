import tqdm

from melo_fwk.rules.ewma import EWMATradingRule
# from rules.sma_rule import SMATradingRule
from melo_fwk.trading_systems import trading_system as ts
from melo_fwk.plots.plots import AccountPlotter
from melo_fwk.datastreams import backtest_data_loader as bdl

import unittest

class TradingSystemUnitTests(unittest.TestCase):

	def test_empty_trading_system(self):
		products = bdl.BacktestDataLoader.get_products("assets/CommodityData/Cocoa_sanitized.csv")
		assert len(products) != 0, "(TradingSystemUnitTests) Did not find any product"
		loaded_prod = bdl.BacktestDataLoader.get_product_datastream(products[0])
		pds = loaded_prod.datastream
		pds.with_daily_returns()

		tr_sys = ts.TradingSystem(
			data_source=pds,
			trading_rules=[],
			forecast_weights=[]
		)

		while not tr_sys.simulation_ended():
			tr_sys.trade_next()

		assert tr_sys.simulation_ended(), "(AssertionError) Simulation not ended"

	def test_trading_system(self):
		"""
		2y 1h :
			goog : 8 32
			googl : 2 8
			meta : 4 16    # mid trends
			aapl : 16 64   # long trends


		:return:
		"""

		products = bdl.BacktestDataLoader.get_products("assets/CommodityData/*_sanitized.csv")
		sum_ = 0.
		for product in tqdm.tqdm(products):
			loaded_prod = bdl.BacktestDataLoader.get_product_datastream(product)
			loaded_prod.datastream.with_daily_returns()

			sma_params = {
				"fast_span": 32,
				"slow_span": 128,
				"scale": 20,
				"cap": 20,
			}
			sma = EWMATradingRule(**sma_params)

			tr_sys = ts.TradingSystem(
				data_source=loaded_prod.datastream,
				trading_rules=[sma],
				forecast_weights=[1.]
			)
			tr_sys.run()

			# print(metrics.AccountMetrics.compute_all_metrics(tr_sys.get_account_series()))
			# orderbook = tr_sys.get_order_book()

			df_account = tr_sys.account_dataframe()
			account_plt = AccountPlotter(df_account, loaded_prod.datastream.get_data())
			account_plt.save_png(f"data/residual/{product['name']}_plot.png")

			sum_ += df_account["Balance"].iloc[-1]

		starting_balance = 10000
		print(f"starting balance : {starting_balance}")
		print(f"final balance : {starting_balance + sum_}")


if __name__ == "__main__":
	unittest.main()
