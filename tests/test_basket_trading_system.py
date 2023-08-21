import unittest
from pathlib import Path

import pandas as pd

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.strat_basket import StratBasket
from melo_fwk.market_data.compo_market_loader import CompositeMarketLoader
from melo_fwk.loggers.console_logger import ConsoleLogger
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.quantfactory_registry import QuantFlowRegistry
from melo_fwk.trading_systems import TradingSystem, TradingSystemIter
from melo_fwk.strategies import EWMAStrategy
from melo_fwk.pose_size import VolTargetInertiaPolicy
from mutils.generic_config_loader import GenericConfigLoader
from melo_fwk.basket.weights import Weights


class TradingSystemUnitTests(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		GenericConfigLoader.setup(str(Path(__file__).parent / "rc/config.json"))
		GlobalLogger.set_loggers([ConsoleLogger])
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)
		QuantFlowRegistry.register_all()
		self.market = CompositeMarketLoader.from_config(GenericConfigLoader.get_node(CompositeMarketLoader.__name__))

	def test_tsys(self):
		self.logger.info("run all at once - TradingSystem")
		self._run_simulation("all", TradingSystem)
		self.logger.info("run each year seperately - TradingSystem")
		self._run_simulation("linear", TradingSystem)

		self.logger.info("run all at once - TradingSystemIter")
		self._run_simulation("all", TradingSystemIter)
		self.logger.info("run each year seperately - TradingSystemIter")
		self._run_simulation("linear", TradingSystemIter)

	def _run_simulation(self, x: str, tr: callable):
		GlobalLogger.set_loggers([ConsoleLogger])

		products = self.market.sample_products(3)
		prod_bsk = ProductBasket(products)
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
				).estimate_forecast_scale(self.market)
			],
			weights=Weights([0.6, 0.4], 1.)
		)

		start_capital = 60000
		size_policy = VolTargetInertiaPolicy(
			annual_vol_target=0.25,
			trading_capital=start_capital)

		trading_subsys = tr(
			product_basket=prod_bsk,
			strat_basket=strat_basket,
			size_policy=size_policy
		)

		if x == "linear":
			results = {
				year: trading_subsys.run_year(year)
				for year in prod_bsk.years()
			}
			balance_sheet = start_capital + pd.DataFrame({y: r.balance_delta_vect() for y, r in results.items()})

		else:  # x == "all":
			tsar = trading_subsys.run()
			balance_sheet = start_capital + tsar.yearly_balance_sheet()

		risk_free = start_capital * ((1 + 0.05) ** 20 - 1)
		self.logger.info(f"starting capital : {start_capital}")
		self.logger.info(f"final balance : {balance_sheet}")
		self.logger.info(f"5% risk free : {risk_free}")

		# tsar_plotter = TsarPlotter({"pname": results})
		# tsar_plotter.save_fig(export_folder="data/residual", mute=True)

	def test_reg(self):
		GlobalLogger.set_loggers([ConsoleLogger])

		products = self.market.sample_products_alpha(1)
		prod_bsk = ProductBasket(products)

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
				).estimate_forecast_scale(self.market)
			],
			weights=Weights([0.6, 0.4], 1.)
		)

		start_capital = 60000
		size_policy = VolTargetInertiaPolicy(
			annual_vol_target=0.25,
			trading_capital=start_capital)

		for prod in prod_bsk.products.values():

			trading_subsys = TradingSystem(
				product_basket=ProductBasket([prod]),
				strat_basket=strat_basket,
				size_policy=size_policy
			)

			ref = trading_subsys.run_product(prod).forecast_series
			df = trading_subsys.run().get_product(prod.name).forecast_series
			flags = ref - df
			flag = flags.mean()
			# print(flag, flags.std())
			assert (flag * 1000).round() <= 2, ""


if __name__ == "__main__":
	unittest.main()
