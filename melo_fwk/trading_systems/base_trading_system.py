import pandas as pd

from melodb.loggers import ILogger
from melodb.Order import Order

from melo_fwk.datastreams.hloc_datastream import HLOCDataStream

from melo_fwk.policies.trading_policies.trading_policy import BaseTradingPolicy, ITradingPolicy
from melo_fwk.policies.vol_target_policies.base_size_policy import ISizePolicy, ConstSizePolicy

from melo_fwk.datastreams.tsar_datastream import TradingSystemAnnualResult

from melo_fwk.market_data.utils.product import Product

class BaseTradingSystem:
	component_name = "BaseTradingSystem"

	def __init__(
		self,
		product: Product,
		trading_rules: list,
		forecast_weights: list,
		size_policy: ISizePolicy = ConstSizePolicy(),
		logger: ILogger = ILogger(component_name)
	):
		self.logger = logger

		assert product is not None, self.logger.error("(AssertionError) Data source is None")
		assert len(trading_rules) == len(forecast_weights), \
			self.logger.error("(AssertionError) Number of TradingRules must match forcast weights")

		self.time_index = 0
		self.order_book = []
		self.tsar_history = []
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

	def order_book_dataframe(self):
		orderbook_dict = [order.to_dict() for order in self.order_book]
		return pd.DataFrame(orderbook_dict)

	def build_tsar(
		self,
		forecast_series: pd.Series,
		pose_series: pd.Series,
		daily_pnl_series: pd.Series):
		return TradingSystemAnnualResult(
			dates=self.hloc_datastream.get_date_series(),
			price_series=self.hloc_datastream.get_close_series(),
			forecast_series=forecast_series,
			size_series=pose_series,
			account_series=daily_pnl_series.expanding(1).sum(),
			daily_pnl_series=daily_pnl_series
		)
