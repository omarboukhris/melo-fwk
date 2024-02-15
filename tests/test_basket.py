import unittest
from pathlib import Path

import pandas as pd

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.strat_basket import StratBasket
from mutils.loggers.console_logger import ConsoleLogger
from mutils.loggers.global_logger import GlobalLogger
from melo_fwk.market_data.compo_market_loader import CompositeMarketLoader
from melo_fwk.pose_size import (
	VolTargetInertiaPolicy,
)
from mutils.quantfactory_registry import QuantFlowRegistry
from melo_fwk.strategies import EWMAStrategy
from mutils.generic_config_loader import GenericConfigLoader
from melo_fwk.basket.weights import Weights


class BasketRegressionUnitTest(unittest.TestCase):

	def init(self):
		GenericConfigLoader.setup(str(Path(__file__).parent / "rc/config.json"))
		self.market = CompositeMarketLoader.from_config(GenericConfigLoader.get_node(CompositeMarketLoader.__name__))

	def test_prod_basket(self):
		self.init()
		for prod in self.market.sample_products_alpha(1.):
			prod_basket = ProductBasket([prod])

			assert (prod_basket.close_df()[prod.name] == prod.get_close_series()).all(), prod.name

	def test_basket_forecast(self):
		self.init()

		for prod in self.market.sample_products_alpha(1.):
			prod_basket = ProductBasket([prod])

			sma_params = {
				"fast_span": 16,
				"slow_span": 64,
				"scale": 16,
			}
			ewma = EWMAStrategy(**sma_params)

			close_df = prod_basket.close_df()
			forecast_df = ewma.forecast_df_cap(close_df).fillna(0)
			# print(forecast_df)

			# compare with tsar forecast series
			for p, col in zip([prod], forecast_df.columns):
				forecast = ewma.forecast_vect_cap(p.get_close_series())
				flag = (forecast[2:] == forecast_df[col][2:]).all()
				# print(flag, col)
				assert flag, p.name

	def test_strat_basket(self):
		self.init()

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

		strat_basket.forecast_cumsum(prod_bsk)


	def test_basket_pose_size(self):
		self.init()

		for prod in self.market.sample_products_alpha(1.):
			prod_basket = ProductBasket([prod])

			sma_params = {
				"fast_span": 16,
				"slow_span": 64,
				"scale": 16,
			}
			ewma = EWMAStrategy(**sma_params)

			close_df = prod_basket.close_df()
			forecast_df = ewma.forecast_df_cap(close_df)

			pose_sizer = VolTargetInertiaPolicy(annual_vol_target=0.4, trading_capital=10000).setup_product_basket(prod_basket)
			pose_df = pose_sizer.position_size_df(forecast_df)
			# print(pose_df)

			# compare with pose_series from tsar as UT
			for p, col in zip([prod], pose_df.columns):
				forecast = ewma.forecast_vect_cap(p.get_close_series())

				pose = pose_sizer.setup_product(p).position_size_vect(forecast)
				flag = (pose[2:] == pose_df[col].round()[2:]).all()
				if flag:
					print(f"done {p.name}")
				else:
					vals = pd.DataFrame({p.name: (pose[2:] - pose_df[col].round()[2:])})
					print(f"errored {p.name} : {vals[vals[p.name] != 0]}")


class BasketUnitTest(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		GenericConfigLoader.setup(str(Path(__file__).parent / "rc/config.json"))
		QuantFlowRegistry.register_all()
		self.market = CompositeMarketLoader.from_config(GenericConfigLoader.get_node(CompositeMarketLoader.__name__))

	def test_prod_basket(self):

		products = self.market.sample_products_alpha(.1)
		prod_basket = ProductBasket(products)

		for prod in products:
			assert (prod_basket.close_df()[prod.name].dropna() == prod.get_close_series()).all(), prod.name

	def test_basket_forecast(self):

		products = self.market.sample_products_alpha(.1)
		prod_basket = ProductBasket(products)

		sma_params = {
			"fast_span": 16,
			"slow_span": 64,
			"scale": 16,
		}
		ewma = EWMAStrategy(**sma_params)

		close_df = prod_basket.close_df()
		forecast_df = ewma.forecast_df_cap(close_df)
		# print(forecast_df)

		# compare with tsar forecast series
		for p, col in zip(products, forecast_df.columns):
			forecast = ewma.forecast_vect_cap(p.get_close_series())
			ref = forecast_df[col][:len(forecast)]
			flag = (forecast[2:] == ref[2:]).all()
			# print(flag, col)
			assert flag, p.name

	def test_basket_pose_size(self):

		products = self.market.sample_products_alpha(.1)
		prod_basket = ProductBasket(products)

		sma_params = {
			"fast_span": 16,
			"slow_span": 64,
			"scale": 16,
		}
		ewma = EWMAStrategy(**sma_params)

		close_df = prod_basket.close_df()
		forecast_df = ewma.forecast_df_cap(close_df)

		pose_sizer = VolTargetInertiaPolicy(annual_vol_target=0.4, trading_capital=10000).setup_product_basket(prod_basket)
		pose_df = pose_sizer.position_size_df(forecast_df)
		# print(pose_df)

		# compare with pose_series from tsar as UT
		for p, col in zip(products, pose_df.columns):
			forecast = ewma.forecast_vect_cap(p.get_close_series())

			pose = pose_sizer.setup_product(p).position_size_vect(forecast)
			ref_pose = pose_df[col][:len(pose)]
			flag = (pose[2:] == ref_pose[2:]).all()
			if flag:
				print(f"done {p.name}")
			else:
				vals = pd.DataFrame({p.name: (pose[2:] - pose_df[col].round()[2:])})
				print(f"errored {p.name} : {vals[vals[p.name] != 0]}")


if __name__ == "__main__":
	unittest.main()
