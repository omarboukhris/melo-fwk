import unittest

import pandas as pd

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.market_data import MarketDataLoader
from melo_fwk.pose_size_vect import (
	VolTargetInertiaPolicy,
	VolTargetSizePolicy
)
from melo_fwk.strategies_vect import EWMAStrategy

from melo_fwk.pose_size import (
	VolTargetInertiaPolicy as VolTargetInertiaPolicy2,
	VolTargetSizePolicy as VolTargetSizePolicy2,
)
from melo_fwk.strategies import EWMAStrategy as EWMAStrategy2

class BasketRegressionUnitTest(unittest.TestCase):

	def test_prod_basket(self):
		for prod in MarketDataLoader.sample_products_alpha(1.):
			prod_basket = ProductBasket([prod])

			assert (prod_basket.close_df()[prod.name] == prod.get_close_series()).all(), prod.name

	def test_basket_forecast(self):
		for prod in MarketDataLoader.sample_products_alpha(1.):
			prod_basket = ProductBasket([prod])

			sma_params = {
				"fast_span": 16,
				"slow_span": 64,
				"scale": 16,
			}
			ewma = EWMAStrategy(**sma_params)

			close_df = prod_basket.close_df()
			forecast_df = ewma.forecast_vect_cap(close_df).fillna(0)
			# print(forecast_df)

			# compare with tsar forecast series
			ewma = EWMAStrategy2(**sma_params)
			for p, col in zip([prod], forecast_df.columns):
				forecast = ewma.forecast_vect_cap(p.get_close_series())
				flag = (forecast[2:] == forecast_df[col][2:]).all()
				# print(flag, col)
				assert flag, p.name

	def test_basket_pose_size(self):
		for prod in MarketDataLoader.sample_products_alpha(1.):
			prod_basket = ProductBasket([prod])

			sma_params = {
				"fast_span": 16,
				"slow_span": 64,
				"scale": 16,
			}
			ewma = EWMAStrategy(**sma_params)

			close_df = prod_basket.close_df()
			forecast_df = ewma.forecast_vect_cap(close_df)

			pose_sizer = VolTargetInertiaPolicy(annual_vol_target=0.4, trading_capital=10000).setup_product_basket(prod_basket)
			pose_df = pose_sizer.position_size_df(forecast_df)
			# print(pose_df)

			# compare with pose_series from tsar as UT
			pose_sizer = VolTargetInertiaPolicy2(annual_vol_target=0.4, trading_capital=10000)
			ewma = EWMAStrategy2(**sma_params)
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

	def test_prod_basket(self):
		products = MarketDataLoader.sample_products_alpha(.1)
		prod_basket = ProductBasket(products)

		for prod in products:
			assert (prod_basket.close_df()[prod.name].dropna() == prod.get_close_series()).all(), prod.name

	def test_basket_forecast(self):
		products = MarketDataLoader.sample_products_alpha(.1)
		prod_basket = ProductBasket(products)

		sma_params = {
			"fast_span": 16,
			"slow_span": 64,
			"scale": 16,
		}
		ewma = EWMAStrategy(**sma_params)

		close_df = prod_basket.close_df()
		forecast_df = ewma.forecast_vect_cap(close_df)
		# print(forecast_df)

		# compare with tsar forecast series
		ewma = EWMAStrategy2(**sma_params)
		for p, col in zip(products, forecast_df.columns):
			forecast = ewma.forecast_vect_cap(p.get_close_series())
			ref = forecast_df[col][:len(forecast)]
			flag = (forecast[2:] == ref[2:]).all()
			# print(flag, col)
			assert flag, p.name

	def test_basket_pose_size(self):
		products = MarketDataLoader.sample_products_alpha(.1)
		prod_basket = ProductBasket(products)

		sma_params = {
			"fast_span": 16,
			"slow_span": 64,
			"scale": 16,
		}
		ewma = EWMAStrategy(**sma_params)

		close_df = prod_basket.close_df()
		forecast_df = ewma.forecast_vect_cap(close_df)

		pose_sizer = VolTargetInertiaPolicy(annual_vol_target=0.4, trading_capital=10000).setup_product_basket(prod_basket)
		pose_df = pose_sizer.position_size_df(forecast_df)
		# print(pose_df)

		# compare with pose_series from tsar as UT
		pose_sizer = VolTargetInertiaPolicy2(annual_vol_target=0.4, trading_capital=10000)
		ewma = EWMAStrategy2(**sma_params)
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
