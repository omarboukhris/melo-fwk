import numpy as np

from melo_fwk.trading_systems import TradingSystemIter, TradingSystem

from melo_fwk.market_data import MarketDataLoader

from melo_fwk.strategies import EWMAStrategy
from melo_fwk.pose_size import VolTargetInertiaPolicy

from melo_fwk.plots import AccountPlotter, TsarPlotter

from melo_fwk.var.VaR import VaR99, VaR95
from melo_fwk.var.CVaR import CVaR97
from melo_fwk.var.SVaR import SVaR99

import pandas as pd
import tqdm
import unittest

class PortfolioUnitTests(unittest.TestCase):

	def test_portfolio(self):
		"""WIP"""
		sma_params = {
			"fast_span": 16,
			"slow_span": 64,
			"scale": 16,
		}
		sma = EWMAStrategy(**sma_params)

		products = MarketDataLoader.get_fx()
		products += MarketDataLoader.get_commodities()
		products = products[:1]

		results = {}
		balance = 0
		start_capital = 10000 * len(products)
		for product in tqdm.tqdm(products):
			loaded_prod = MarketDataLoader.load_datastream(product)
			size_policy = VolTargetInertiaPolicy(
				annual_vol_target=0.4,
				trading_capital=10000)

			tr_sys = TradingSystemIter(
				product=loaded_prod,
				trading_rules=[sma],
				forecast_weights=[1.],
				size_policy=size_policy
			)

			# simulation with constant risk
			tsar = tr_sys.run()

			results.update({product["name"]: tsar})
			balance += tsar.balance_delta()

		# plot whole balance
		results_list = [r for r in results.values()]
		account_df = pd.DataFrame()

		risk_free = start_capital * ((1 + 0.05) ** 20 - 1)
		print(f"starting capital : {start_capital}")
		print(f"final balance : {balance}")
		print(f"5% risk free : {risk_free}")

		for p, tsar in zip(products, results_list):
			lp = MarketDataLoader.load_datastream(p)
			account_df[lp.name] = tsar.account_series
		n=1
		var_class_ = VaR99
		var99 = var_class_(n, 10000, model="sim_path")
		print(var99(
			account_df,
			np.array([1/len(products) for _ in range(len(products))]),
		))

		var99 = var_class_(n, 10000, model="single_sim")
		print(var99(
			account_df,
			np.array([1/len(products) for _ in range(len(products))]),
		))

		var99 = var_class_(n, 0.8, method="histo", model="sim_path")
		print(var99(
			account_df,
			np.array([1/len(products) for _ in range(len(products))]),
		))

		var99 = var_class_(n, 0.8, method="histo", model="single_sim")
		print(var99(
			account_df,
			np.array([1/len(products) for _ in range(len(products))]),
		))

		var99 = var_class_(n, None, method="param")
		print(var99(
			account_df,
			np.array([1/len(products) for _ in range(len(products))]),
		))

		# account_plt = AccountPlotter(account_df)
		# account_plt.save_png(f"data/residual/all_plot_vect.png")

		# plot tsar
		# tsar_plotter = TsarPlotter({"pname": results})
		# tsar_plotter.save_fig(export_folder="data/residual")
		# return results_list


if __name__ == "__main__":
	unittest.main()
