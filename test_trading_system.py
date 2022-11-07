import sys
import unittest

import numpy as np
from tqdm import tqdm

from melo_fwk.market_data import CommodityDataLoader
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.strategies import EWMAStrategy
from melo_fwk.policies.size import VolTargetInertiaPolicy
from melo_fwk.plots import TsarPlotter

class TradingSystemUnitTests(unittest.TestCase):

	def test_trading_system(self):
		TradingSystemUnitTests.run_simulation("all")
		TradingSystemUnitTests.run_simulation("linear")
		TradingSystemUnitTests.run_simulation("compound")

	@staticmethod
	def run_simulation(x: str):
		product = CommodityDataLoader.Gold
		# product = FxDataLoader.EURUSD

		strat = [
			EWMAStrategy(
				fast_span=16,
				slow_span=64,
				scale=16.,
			),
			EWMAStrategy(
				fast_span=8,
				slow_span=32,
				scale=10.,
			)
		]
		fw = [0.6, 0.4]

		start_capital = 60000
		size_policy = VolTargetInertiaPolicy(
			annual_vol_target=25e-2,
			trading_capital=start_capital)

		trading_subsys = TradingSystem(
			product=product,
			trading_rules=strat,
			forecast_weights=fw,
			size_policy=size_policy
		)

		results = {}

		if x == "compound":
			results = {
				f"Gold_{y}_it": tsar
				for y, tsar in zip(product.years(), trading_subsys.compound_by_year())
			}

		elif x == "linear":
			results = {
				f"Gold_{year}_it": trading_subsys.run_year(year)
				for year in product.years()
			}

		elif x == "all":
			tsar = trading_subsys.run()
			results = {
				f"Gold_{year}_it": tsar.get_year(year)
				for year in product.years()
			}

		balance = start_capital + np.sum([r.balance_delta() for r in results.values()])
		risk_free = start_capital * ((1 + 0.05) ** 20 - 1)
		print(f"starting capital : {start_capital}")
		print(f"final balance : {balance}")
		print(f"5% risk free : {risk_free}")

		tsar_plotter = TsarPlotter({"pname": results})
		tsar_plotter.save_fig(export_folder="data/residual", mute=True)


if __name__ == "__main__":
	unittest.main()
