import numpy as np

from melo_fwk.market_data.product import Product

from melo_fwk.strategies import BaseStrategy

from melo_fwk.size_policies import BaseSizePolicy

from melo_fwk.datastreams import (
	HLOCDataStream,
	TsarDataStream
)
from typing import List

import pandas as pd

class BaseTradingSystem:

	def __init__(
		self,
		product: Product,
		trading_rules: List[BaseStrategy],
		forecast_weights: List[float],
		size_policy: BaseSizePolicy = BaseSizePolicy(),
	):

		assert product is not None, "(AssertionError) Data source is None"
		assert len(trading_rules) == len(forecast_weights), \
			"(AssertionError) Number of TradingRules must match forcast weights"

		self.time_index = 0
		self.product = product
		self.trading_rules = trading_rules
		self.forecast_weights = forecast_weights
		self.size_policy = size_policy.setup_product(self.product)

	@staticmethod
	def default():
		return BaseTradingSystem(
			product=HLOCDataStream.get_empty(),
			trading_rules=[],
			forecast_weights=[]
		)

	def forecast_cumsum(self):
		f_series = pd.Series(np.zeros(shape=(len(self.product.get_dataframe()))))

		for trading_rule, forecast_weight in zip(self.trading_rules, self.forecast_weights):
			f_series += forecast_weight * trading_rule.forecast_vect_cap(self.product.get_close_series())

		return f_series

	def build_tsar(
		self,
		forecast_series: pd.Series,
		pose_series: pd.Series,
		daily_pnl_series: pd.Series
	):
		return TsarDataStream(dataframe=pd.DataFrame({
			"Date": self.product.get_date_series(),
			"Price": self.product.get_close_series(),
			"Forecast": forecast_series,
			"Size": pose_series,
			"Account": daily_pnl_series.expanding(1).sum(),
			"Daily_PnL": daily_pnl_series
		}))
