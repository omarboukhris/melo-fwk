import numpy as np

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.results_basket import ResultsBasket

from melo_fwk.strategies_vect import BaseStrategy

from melo_fwk.pose_size_vect import BaseSizePolicy

from melo_fwk.datastreams import (
	HLOCDataStream,
	TsarDataStream
)
from typing import List

import pandas as pd

class BaseTradingSystem:

	def __init__(
		self,
		product_basket: ProductBasket,
		trading_rules: List[BaseStrategy],
		forecast_weights: List[float],
		size_policy: BaseSizePolicy = BaseSizePolicy(0., 0.),
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

	def forecast_cumsum(self):
		f_df = pd.DataFrame({
			p.name: np.zeros(shape=len(self.product_basket.close_df()))
			for p in self.product_basket.products
		})

		for trading_rule, forecast_weight in zip(self.trading_rules, self.forecast_weights):
			f_df += forecast_weight * trading_rule.forecast_vect_cap(self.product_basket.close_df())

		return f_df

	def update_trading_capital(self, delta: float):
		self.size_policy.update_trading_capital(delta)

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

	def build_tsar(
		self,
		forecast_df: pd.DataFrame,
		pose_df: pd.DataFrame,
		daily_pnl_df: pd.DataFrame
	) -> ResultsBasket:
		results_list = []
		for product in self.product_basket.products:
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
