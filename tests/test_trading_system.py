import unittest

import numpy as np

from melo_fwk.loggers.console_logger import ConsoleLogger
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.market_data import CommodityDataLoader
from melo_fwk.plots import TsarPlotter

from minimelo.trading_systems import TradingSystem, TradingSystemIter
from minimelo.strategies import EWMAStrategy
from minimelo.pose_size import VolTargetInertiaPolicy


class TradingSystemUnitTests(unittest.TestCase):

	def init(self):
		GlobalLogger.set_loggers([ConsoleLogger])
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)

	def runTest(self):
		self.init()
		self.logger.info("run all at once - TradingSystem")
		self._run_simulation("all", TradingSystem)
		self.logger.info("run each year seperately - TradingSystem")
		self._run_simulation("linear", TradingSystem)
		self.logger.info("run compounded by year - TradingSystem")
		self._run_simulation("compound", TradingSystem)

		self.logger.info("run all at once - TradingSystemIter")
		self._run_simulation("all", TradingSystemIter)
		self.logger.info("run each year seperately - TradingSystemIter")
		self._run_simulation("linear", TradingSystemIter)
		self.logger.info("run compounded by year - TradingSystemIter")
		self._run_simulation("compound", TradingSystemIter)

	def _run_simulation(self, x: str, tr: callable):
		GlobalLogger.set_loggers([ConsoleLogger])

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
			).estimate_forecast_scale()
		]
		fw = [0.6, 0.4]

		start_capital = 60000
		size_policy = VolTargetInertiaPolicy(
			annual_vol_target=25e-2,
			trading_capital=start_capital)

		trading_subsys = tr(
			product=product,
			trading_rules=strat,
			forecast_weights=fw,
			size_policy=size_policy
		)

		results = {}

		if x == "compound":
			results = {
				f"{tr.__name__}_Gold_{y}_it": tsar
				for y, tsar in zip(product.years(), trading_subsys.compound_by_year())
			}

		elif x == "linear":
			results = {
				f"{tr.__name__}_Gold_{year}_it": trading_subsys.run_year(year)
				for year in product.years()
			}

		elif x == "all":
			tsar = trading_subsys.run()
			results = {
				f"{tr.__name__}_Gold_{year}_it": tsar.get_year(year)
				for year in product.years()
			}

		balance = start_capital + np.sum([r.balance_delta() for r in results.values()])
		risk_free = start_capital * ((1 + 0.05) ** 20 - 1)
		self.logger.info(f"starting capital : {start_capital}")
		self.logger.info(f"final balance : {balance}")
		self.logger.info(f"5% risk free : {risk_free}")

		tsar_plotter = TsarPlotter({"pname": results})
		tsar_plotter.save_fig(export_folder="data/residual", mute=True)


if __name__ == "__main__":
	unittest.main()
