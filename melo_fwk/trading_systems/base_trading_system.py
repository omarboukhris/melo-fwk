import numpy as np

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.results_basket import ResultsBasket
from melo_fwk.market_data.product import Product

from melo_fwk.strategies import BaseStrategy

from melo_fwk.pose_size import BaseSizePolicy

from melo_fwk.datastreams import (
	HLOCDataStream,
	TsarDataStream
)
from typing import List

import pandas as pd

class BaseTradingSystem:

	def __init__(
		self,
		trading_rules: List[BaseStrategy],
		forecast_weights: List[float],
		size_policy: BaseSizePolicy = BaseSizePolicy(0., 0.),
		product_basket: ProductBasket = ProductBasket([]),
	):

		assert len(trading_rules) == len(forecast_weights), \
			"(AssertionError) Number of TradingRules must match forcast weights"

		self.time_index = 0
		self.product_basket = product_basket
		self.trading_rules = trading_rules
		self.forecast_weights = forecast_weights
		self.size_policy = size_policy.setup_product_basket(product_basket)

	@staticmethod
	def default():
		return BaseTradingSystem(
			product_basket=ProductBasket([HLOCDataStream.get_empty()]),
			trading_rules=[],
			forecast_weights=[]
		)

	def forecast_cumsum_product(self, product: Product):
		f_series = np.array([0.] * len(product.get_close_series()))

		for trading_rule, forecast_weight in zip(self.trading_rules, self.forecast_weights):
			f_series += forecast_weight * trading_rule.forecast_vect_cap(product.get_close_series()).to_numpy()

		return pd.Series(f_series)

	def forecast_cumsum(self):
		f_df = pd.DataFrame({
			p.name: np.zeros(shape=len(self.product_basket.close_df()))
			for p in self.product_basket.products.values()
		})

		for trading_rule, forecast_weight in zip(self.trading_rules, self.forecast_weights):
			f_df += forecast_weight * trading_rule.forecast_df_cap(self.product_basket.close_df())

		return f_df

	def update_trading_capital(self, delta: float):
		self.size_policy.update_trading_capital(delta)

	def run_product(self, product: Product) -> TsarDataStream:
		pass

	def run(self) -> ResultsBasket:
		pass

	def run_year(self, year: int, stitch: bool = False) -> ResultsBasket:
		product_basket = self.product_basket
		self.product_basket = self.product_basket.get_year(year, stitch)
		self.size_policy.setup_product_basket(self.product_basket)
		try:
			results = self.run()
			return results if stitch else results.get_year(year)
		finally:
			self.product_basket = product_basket

	def run_product_year(self, product: Product, year: int, stitch: bool = False):
		product = product.get_year(year, stitch)
		self.size_policy.setup_product(product)
		return self.run_product(product).get_year(year) if stitch else self.run_product(product)

	def compound_product_by_year(self, product: Product, stitch: bool = False):
		output = []
		for year in product.years():
			tsar = self.run_product_year(product, year, stitch)
			self.update_trading_capital(tsar.balance_delta())
			output.append(tsar)
		return output

	@staticmethod
	def build_tsar(
		product: Product,
		forecast_series: pd.Series,
		pose_series: pd.Series,
		daily_pnl_series: pd.Series
	) -> TsarDataStream:
		return TsarDataStream(
			name=product.name,
			dataframe=pd.DataFrame({
				"Date": product.get_date_series().reset_index(drop=True),
				"Price": product.get_close_series().reset_index(drop=True),
				"Forecast": forecast_series,
				"Size": pose_series,
				"Account": daily_pnl_series.expanding(1).sum(),
				"Daily_PnL": daily_pnl_series
			})
		)

	def build_tsar_basket(
		self,
		forecast_df: pd.DataFrame,
		pose_df: pd.DataFrame,
		daily_pnl_df: pd.DataFrame
	) -> ResultsBasket:
		results_list = []
		for product in self.product_basket.products.values():
			results_list.append(TsarDataStream(
				name=product.name,
				dataframe=pd.DataFrame({
					"Date": product.get_date_series().reset_index(drop=True),
					"Price": product.get_close_series().reset_index(drop=True),
					"Forecast": forecast_df[product.name],
					"Size": pose_df[product.name],
					"Account": daily_pnl_df[product.name].expanding(1).sum(),
					"Daily_PnL": daily_pnl_df[product.name]
				})
			))
		return ResultsBasket(results_list)
