
from melo_fwk.market_data.product import Product

from melo_fwk.strategies import BaseStrategy

from melo_fwk.size_policies import BaseSizePolicy

from melodb.loggers import ILogger

from melo_fwk.datastreams import (
	HLOCDataStream,
	TsarDataStream
)
from typing import List

import pandas as pd

class BaseTradingSystem:
	component_name = "BaseTradingSystem"

	def __init__(
		self,
		product: Product,
		trading_rules: List[BaseStrategy],
		forecast_weights: List[float],
		size_policy: BaseSizePolicy = BaseSizePolicy(),
		logger: ILogger = ILogger(component_name)
	):
		self.logger = logger

		assert product is not None, self.logger.error("(AssertionError) Data source is None")
		assert len(trading_rules) == len(forecast_weights), \
			self.logger.error("(AssertionError) Number of TradingRules must match forcast weights")

		self.time_index = 0
		self.hloc_datastream = product.datastream
		self.trading_rules = trading_rules
		self.forecast_weights = forecast_weights
		self.size_policy = size_policy
		self.block_size = product.block_size

	@staticmethod
	def default():
		return BaseTradingSystem(
			product=HLOCDataStream.get_empty(),
			trading_rules=[],
			forecast_weights=[]
		)

	def build_tsar(
		self,
		forecast_series: pd.Series,
		pose_series: pd.Series,
		daily_pnl_series: pd.Series
	):
		return TsarDataStream(dataframe=pd.DataFrame({
			"Date": self.hloc_datastream.get_date_series(),
			"Price": self.hloc_datastream.get_close_series(),
			"Forecast": forecast_series,
			"Size": pose_series,
			"Account": daily_pnl_series.expanding(1).sum(),
			"Daily_PnL": daily_pnl_series
		}))
