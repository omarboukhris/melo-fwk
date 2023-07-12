import unittest
from pathlib import Path

import numpy as np

from melo_fwk.basket.strat_basket import StratBasket
from melo_fwk.market_data.market_data_loader import MarketDataLoader
from melo_fwk.loggers.console_logger import ConsoleLogger
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.plots import TsarPlotter
from melo_fwk.quantfactory_registry import QuantFlowRegistry

from melo_fwk.trading_systems import TradingSystem, TradingSystemIter
from melo_fwk.strategies import EWMAStrategy
from melo_fwk.pose_size import VolTargetInertiaPolicy
from melo_fwk.utils.generic_config_loader import GenericConfigLoader
from melo_fwk.utils.weights import Weights


class TradingSystemUnitTests(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		GenericConfigLoader.setup(str(Path(__file__).parent / "rc/config.json"))
		GlobalLogger.set_loggers([ConsoleLogger])
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)
		QuantFlowRegistry.register_all()

	def runTest(self):
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

		market_loader = MarketDataLoader()
		product = market_loader.get("Commodities", "Gold")

		# product = FxDataLoader.EURUSD

		strat_basket = StratBasket(
			strat_list=[
				EWMAStrategy(
					fast_span=16,
					slow_span=64,
					scale=16.,
				),
				EWMAStrategy(
					fast_span=8,
					slow_span=32,
				).estimate_forecast_scale(MarketDataLoader())
			],
			weights=Weights([0.6, 0.4], 1.)
		)

		start_capital = 60000
		size_policy = VolTargetInertiaPolicy(
			annual_vol_target=25e-2,
			trading_capital=start_capital)

		trading_subsys = tr(
			strat_basket=strat_basket,
			size_policy=size_policy
		)

		results = {}

		if x == "compound":
			results = {
				f"{tr.__name__}_Gold_{y}_it": tsar
				for y, tsar in zip(product.years(), trading_subsys.compound_product_by_year(product))
			}

		elif x == "linear":
			results = {
				f"{tr.__name__}_Gold_{year}_it": trading_subsys.run_product_year(product, year)
				for year in product.years()
			}

		elif x == "all":
			tsar = trading_subsys.run_product(product)
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
