import pandas as pd
import tqdm

from melo_fwk.plots.tsar_plots import TsarPlotter
from melo_fwk.policies.vol_target_policies.vol_target import VolTarget
from melo_fwk.policies.vol_target_policies.vol_target_size_policy import VolTargetSizePolicy
from melo_fwk.rules.ewma import EWMATradingRule
# from rules.sma_rule import SMATradingRule
from melo_fwk.trading_systems import trading_system as ts
from melo_fwk.trading_systems import trading_vect_system as tv
from melo_fwk.plots.plots import AccountPlotter
from melo_fwk.market_data.utils import market_data_loader as bdl

import unittest

class TradingSystemUnitTests(unittest.TestCase):

	def test_empty_trading_system(self):
		products = bdl.MarketDataLoader.get_dataset_locations("assets/Commodity/Cocoa.csv")
		assert len(products) != 0, "(TradingSystemUnitTests) Did not find any product"
		loaded_prod = bdl.MarketDataLoader.load_datastream(products[0])
		pds = loaded_prod.datastream
		pds._with_daily_returns()

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

		products = bdl.MarketDataLoader.get_commodities()
		sum_ = 0.
		for product in tqdm.tqdm(products):
			loaded_prod = bdl.MarketDataLoader.load_datastream(product)
			loaded_prod.datastream._with_daily_returns()

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

			df_account = tr_sys.account_dataframe()
			account_plt = AccountPlotter(df_account, loaded_prod.datastream.get_data())
			account_plt.save_png(f"data/residual/{product['name']}_plot.png")

			sum_ += df_account["Balance"].iloc[-1]

		starting_balance = 10000
		print(f"starting balance : {starting_balance}")
		print(f"final balance : {starting_balance + sum_}")

	def test_trading_system_vect(self):
		"""
		2y 1h :
			goog : 8 32
			googl : 2 8
			meta : 4 16    # mid trends
			aapl : 16 64   # long trends


		:return:
		"""

		products = bdl.MarketDataLoader.get_fx()
		products += bdl.MarketDataLoader.get_commodities()
		sum_ = 0.
		results = {}

		for product in tqdm.tqdm(products):
			loaded_prod = bdl.MarketDataLoader.load_datastream(product)
			loaded_prod.datastream._with_daily_returns()

			sma_params = {
				"fast_span": 16,
				"slow_span": 64,
				"scale": 12,
				"cap": 20,
			}
			sma = EWMATradingRule(**sma_params)
			vol_target = VolTarget(
				annual_vol_target=0.5,
				trading_capital=10000)
			size_policy = VolTargetSizePolicy(risk_policy=vol_target)

			tr_sys = tv.TradingVectSystem(
				data_source=loaded_prod.datastream,
				trading_rules=[sma],
				forecast_weights=[1.],
				size_policy=size_policy
			)
			tr_sys.trade_vect()

			# df_account = tr_sys.account_dataframe()
			# account_plt = AccountPlotter(df_account, loaded_prod.datastream.get_data())
			# account_plt.save_png(f"data/residual/{product['name']}_plot_vect.png")

			tsar = tr_sys.get_tsar()
			results.update({product["name"]: tsar})
			sum_ += tsar.annual_delta()

		results_list = [r for r in results.values()]
		account_df = pd.DataFrame({
			"Date": results_list[0].dates,
			"Balance": [0. for _ in results_list[0].dates]
		})
		for tsar in results_list:
			account_df["Balance"] += tsar.account_series
		account_plt = AccountPlotter(account_df)
		account_plt.save_png(f"data/residual/all_plot_vect.png")

		tsar_plotter = TsarPlotter({"pname": results})
		tsar_plotter.save_fig(export_folder="data/residual")

		starting_balance = 10000 * len(results)
		print(f"starting balance : {starting_balance}")
		print(f"final balance : {sum_}")


if __name__ == "__main__":
	unittest.main()
