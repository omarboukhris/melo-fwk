import pandas as pd

from melodb.loggers import ILogger
from melodb.Order import Order

from melo_fwk.datastreams.hloc_datastream import HLOCDataStream

from melo_fwk.policies.trading_policy import BaseTradingPolicy, ITradingPolicy
from melo_fwk.policies.vol_target_policy import ConstSizePolicy, ISizePolicy

from melo_fwk.metrics.metrics import AccountMetrics

from melo_fwk.trading_systems.tsar import TradingSystemAnnualResult


class BaseTradingSystem:
	component_name = "BaseTradingSystem"

	def __init__(
		self,
		data_source: HLOCDataStream,
		trading_rules: list,
		forecast_weights: list,
		size_policy: ISizePolicy = ConstSizePolicy(),
		trading_policy: ITradingPolicy = BaseTradingPolicy(),
		logger: ILogger = ILogger(component_name)
	):
		self.logger = logger

		assert data_source is not None, self.logger.error("(AssertionError) Data source is None")
		assert len(trading_rules) == len(forecast_weights), \
			self.logger.error("(AssertionError) Number of TradingRules must match forcast weights")

		self.time_index = 0
		self.order_book = []
		self.tsar_history = None
		self.current_trade = Order.empty()
		self.data_source = data_source
		self.trading_rules = trading_rules
		self.forecast_weights = forecast_weights
		self.size_policy = size_policy
		self.trading_policy = trading_policy

	@staticmethod
	def default():
		return BaseTradingSystem(
			data_source=HLOCDataStream.get_empty(),
			trading_rules=[],
			forecast_weights=[]
		)


	def dates_df(self):
		return pd.DataFrame(self.tsar_history)["Date"]

	def order_book_dataframe(self):
		orderbook_dict = [order.to_dict() for order in self.order_book]
		return pd.DataFrame(orderbook_dict)

	def forecast_dataframe(self):
		return pd.DataFrame(self.tsar_history)[["Date", "Forecast"]]

	def forecast_series(self):
		return pd.DataFrame(self.tsar_history)["Forecast"]

	def account_dataframe(self):
		return pd.DataFrame(self.tsar_history)[["Date", "Balance"]]

	def account_series(self):
		return pd.DataFrame(self.tsar_history)["Balance"]

	def position_dataframe(self):
		return pd.DataFrame(self.tsar_history)[["Date", "PositionSize"]]

	def position_series(self):
		return pd.DataFrame(self.tsar_history)["PositionSize"]

	def price_series(self):
		return pd.DataFrame(self.tsar_history)["Price"]

	def get_tsar(self):
		return TradingSystemAnnualResult(
			vol_target=self.size_policy.risk_policy,
			account_metrics=AccountMetrics(self.account_series()),
			dates=self.dates_df(),
			price_series=self.price_series(),
			forecast_series=self.forecast_series(),
			size_series=self.position_series(),
			account_series=self.account_series()
		)

	def get_negative_tsar(self):
		return TradingSystemAnnualResult(
			vol_target=self.size_policy.risk_policy,
			account_metrics=AccountMetrics(self.account_series()*-1),
			dates=self.dates_df(),
			price_series=self.price_series(),
			forecast_series=self.forecast_series(),
			size_series=self.position_series(),
			account_series=self.account_series()*-1
		)
