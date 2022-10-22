from melo_fwk.trading_systems import TradingSystem

from melo_fwk.market_data import MarketDataLoader

from melo_fwk.strategies import (
	EWMAStrategy,
	# SMAStrategy
)
from melo_fwk.size_policies import VolTargetInertiaPolicy
from melo_fwk.size_policies.vol_target import VolTarget

from melo_fwk.plots import AccountPlotter, TsarPlotter

import numpy as np
import pandas as pd
import tqdm
import unittest

class TradingSystemUnitTests(unittest.TestCase):

	def test_trading_system_vect(self):
		"""
		2y 1h :
			goog : 8 32
			googl : 2 8
			meta : 4 16    # mid trends
			aapl : 16 64   # long trends

		:return:
		"""

		products = MarketDataLoader.get_fx()
		products += MarketDataLoader.get_commodities()
		# products = random.sample(products, 20)
		sum_ = 0.
		results = {}

		for product in tqdm.tqdm(products):
			loaded_prod = MarketDataLoader.load_datastream(product)

			sma_params = {
				"fast_span": 16,
				"slow_span": 64,
				"scale": 16,
			}
			sma = EWMAStrategy(**sma_params)
			vol_target = VolTarget(
				annual_vol_target=0.5,
				trading_capital=50000)
			size_policy = VolTargetInertiaPolicy(
				risk_policy=vol_target,
				block_size=loaded_prod.block_size)

			tr_sys = TradingSystem(
				product=loaded_prod,
				trading_rules=[sma],
				forecast_weights=[1.],
				size_policy=size_policy
			)
			tsar = tr_sys.run()

			results.update({product["name"]: tsar})
			sum_ += tsar.annual_delta()

		# results_list = self.plot_all(results)
		#
		# starting_balance = 50000 * len(results)
		# forecasts = [tsar.forecast_series.mean() for tsar in results_list]
		# print(f"starting balance : {starting_balance}")
		# print(f"final balance : {sum_}")
		# print(f"forecast means {np.mean(forecasts)}: {forecasts}")

	def plot_all(self, results):
		# plot whole balance
		results_list = [r for r in results.values()]
		account_df = pd.DataFrame({
			"Date": results_list[0].dates,
			"Balance": [0. for _ in results_list[0].dates]
		})
		for tsar in results_list:
			account_df["Balance"] += tsar.account_series
		account_plt = AccountPlotter(account_df)
		account_plt.save_png(f"data/residual/all_plot_vect.png")

		# plot tsar
		tsar_plotter = TsarPlotter({"pname": results})
		tsar_plotter.save_fig(export_folder="data/residual")
		return results_list


if __name__ == "__main__":
	unittest.main()
