import pandas as pd

from melodb.loggers import ILogger
from melodb.Order import Order

from melo_fwk.market_data.utils.hloc_datastream import HLOCDataStream

from melo_fwk.policies.trading_policies.trading_policy import BaseTradingPolicy, ITradingPolicy
from melo_fwk.policies.vol_target_policies.base_size_policy import ISizePolicy, ConstSizePolicy

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
		self.tsar_history = []
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


	def dates_dataframe(self):
		return pd.DataFrame(self.tsar_history)["Date"]

	def order_book_dataframe(self):
		orderbook_dict = [order.to_dict() for order in self.order_book]
		return pd.DataFrame(orderbook_dict)

	def forecast_dataframe(self):
		return pd.DataFrame(self.tsar_history)[["Date", "Forecast"]]

	def forecast_series(self):
		return pd.DataFrame(self.tsar_history)["Forecast"]

	def daily_pnl_dataframe(self):
		return pd.DataFrame(self.tsar_history)[["Date", "Daily_PnL"]]

	def daily_pnl_series(self):
		return pd.DataFrame(self.tsar_history)["Daily_PnL"]

	def account_dataframe(self):
		return pd.DataFrame({
			"Date": self.dates_dataframe(),
			"Balance": self.account_series(),
		})

	def account_series(self):
		daily_pnl = self.daily_pnl_series()
		# daily_balance = [daily_pnl.iloc[:i].cumsum() for i in range(len(daily_pnl))]
		return daily_pnl.expanding(1).sum()

	def position_dataframe(self):
		return pd.DataFrame(self.tsar_history)[["Date", "PositionSize"]]

	def position_series(self):
		return pd.DataFrame(self.tsar_history)["PositionSize"]

	def price_series(self):
		return pd.DataFrame(self.tsar_history)["Price"]

	def get_tsar(self):
		return TradingSystemAnnualResult(
			vol_target=self.size_policy.risk_policy,
			dates=self.dates_dataframe(),
			price_series=self.price_series(),
			forecast_series=self.forecast_series(),
			size_series=self.position_series(),
			account_series=self.account_series(),
			daily_pnl_series=self.daily_pnl_series()
		)

	def get_negative_tsar(self):
		return TradingSystemAnnualResult(
			vol_target=self.size_policy.risk_policy,
			dates=self.dates_dataframe(),
			price_series=self.price_series(),
			forecast_series=self.forecast_series(),
			size_series=self.position_series(),
			account_series=self.account_series() * -1,
			daily_pnl_series=self.daily_pnl_series() * -1
		)
