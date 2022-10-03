
import pandas as pd
import tqdm
from rules.ewma_rule import EWMATradingRule
# from rules.sma_rule import SMATradingRule
from process import trading_system as ts
from helpers.plots import ForecastPlotter, AccountPlotter
from datastreams import datastream as ds, backtest_data_loader as bdl

import unittest

class TradingSystemUnitTests(unittest.TestCase):
	def test_empty_trading_system(self):
		df = pd.read_csv("data/CommodityData/Cocoa_sanitized.csv")

		pds = ds.HLOCDataStream(dataframe=df)

		tr_sys = ts.TradingSystem(
			balance=10000,
			data_source=pds,
			trading_rules=[],
			forecast_weights=[]
		)

		while not tr_sys.simulation_ended():
			tr_sys.trade_next()

		assert tr_sys.simulation_ended(), "(AssertionError) Simulation not ended"


	def test_datastream(self):
		def process_tick(_):
			pass

		pdstream = ds.HLOCDataStream(
			dataframe=pd.read_csv("data/CommodityData/Cocoa_sanitized.csv"))

		for tick in pdstream:
			process_tick(tick)

	def test_trading_rule(self):
		products = bdl.BacktestDataLoader.get_products("data/CommodityData/*_sanitized.csv")
		for p in tqdm.tqdm(products):
			TradingLoopHelper.run_trading_rule_loop(p)


	def test_trading_system(self):
		"""
		2y 1h :
			goog : 8 32
			googl : 2 8
			meta : 4 16    # mid trends
			aapl : 16 64   # long trends


		:return:
		"""

		# df = pd.read_csv("data/Commodity Data/Gold_sanitized.csv")
		# products = bdl.BacktestDataLoader.get_products("data/Stocks/GOOG_1d_10y.csv")
		products = bdl.BacktestDataLoader.get_products("data/CommodityData/*_sanitized.csv")
		sum_ = 0.
		for p in tqdm.tqdm(products):
			df_account = TradingLoopHelper.run_trading_loop(p)
			sum_ += df_account["Balance"].iloc[-1]
		starting_balance = 10000
		print(f"starting balance : {starting_balance}")
		print(f"final balance : {starting_balance + sum_}")

class TradingLoopHelper:
	@staticmethod
	def run_trading_rule_loop(product):

		df, pds = bdl.BacktestDataLoader.get_product_datastream(product)
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

		# forcast_df = pd.DataFrame(output_forcast)
		# acc_plt = ForecastPlotter(forcast_df, df)
		# acc_plt.save_png(f"data/residual/{product['name']}_plot.png")
		# acc_plt.show()

		# price_plt = PricePlotter(df)
		# price_plt.plot()
		# price_plt.save_png("data/residual/test_trading_rule__price_plot")
		# price_plt.show()

	@staticmethod
	def run_trading_loop(product):
		df, pds = bdl.BacktestDataLoader.get_product_datastream(product)
		pds.with_daily_returns()

		sma_params = {
			"fast_span": 32,
			"slow_span": 128,
			"scale": 20,
			"cap": 20,
		}
		sma = EWMATradingRule(**sma_params)

		tr_sys = ts.TradingSystem(
			balance=0,
			data_source=pds,
			trading_rules=[sma],
			forecast_weights=[1.]
		)
		tr_sys.run()

		# print(tr_sys.sharpe_ratio())
		# orderbook = tr_sys.get_order_book()

		df_account = tr_sys.get_account_history()
		# account_plt = AccountPlotter(df_account, df)
		# account_plt.add_vlines(orderbook)
		# account_plt.save_png(f"data/residual/{product['name']}_plot.png")
		# account_plt.show()
		# df_account.to_csv("test_results/account.csv")
		# orderbook.to_csv("test_results/book.csv")
		return df_account



if __name__ == "__main__":
	unittest.main()
