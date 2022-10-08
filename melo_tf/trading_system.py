
import numpy as np
import pandas as pd
import tqdm

from melodb.loggers import ILogger
from melodb.Order import Order

from melo_tf.datastreams.datastream import HLOCDataStream
from melo_tf.policies.trading_policy import BaseTradingPolicy, ITradingPolicy
from melo_tf.policies.vol_target_policy import ConstSizePolicy, ISizePolicy


class TradingSystem:
	"""Class for backtesting offline a trading system.
	This class trades only one position, one product at a time.
	To backtest for a whole portfolio, you need a TradingSystem per asset,
	then sum up after each iteration.
	Sub-classes can implement multi-threaded execution if needed.

	TODO:
		Implement an TradeExecutor to execute trades online (demo/live) and offline (backtest)
		=> warping of open/close_trade methods

	Needs :
	- a data source for historic price data
	- a set of trading rules
	- a set of forcast weights (sum(w_i) == 1)
	- a policy for entering/exiting trades
	"""

	component_name = "TradingSystem"

	def __init__(
		self,
		balance: float,
		data_source: HLOCDataStream,
		trading_rules: list,
		forecast_weights: list,
		size_policy: ISizePolicy = ConstSizePolicy(),
		trading_policy: ITradingPolicy = BaseTradingPolicy(),  # add it later to mql
		logger: ILogger = ILogger(component_name)
	):
		self.logger = logger
		if logger is not None:
			self.logger = ILogger(TradingSystem.component_name)

		assert data_source is not None, self.logger.error("(AssertionError) Data source is None")
		assert len(trading_rules) == len(forecast_weights), \
			self.logger.error("(AssertionError) Number of TradingRules must match forcast weights")

		self.accout = [
			{
				"Date": data_source.get_current_date(),
				"Balance": balance,
			}
		]
		self.time_index = 0
		self.order_book = []
		self.forecast_history = []
		self.pose_size_history = []
		self.current_trade = Order.empty()
		self.data_source = data_source
		self.trading_rules = trading_rules
		self.forecast_weights = forecast_weights
		self.size_policy = size_policy
		self.trading_policy = trading_policy

	@staticmethod
	def default():
		return TradingSystem.start(0)

	@staticmethod
	def start(balance: float):
		return TradingSystem(
			balance=balance,
			data_source=HLOCDataStream.get_empty(),
			trading_rules=[],
			forecast_weights=[]
		)

	def reset(self):
		self.time_index = 0
		self.order_book = []
		self.forecast_history = []
		self.current_trade = Order.empty()

	def open_trade(self, forecast: float, size: float, entry_time: str):
		# adjust vol target and update size policy object ?
		self.current_trade.open_trade(forecast, size, entry_time)

		# submit open order

		self.logger.info(f"Opened Trade {self.current_trade}")

	def close_trade(self, forecast: float, exit_time: str):
		self.current_trade.close_trade(forecast, exit_time)
		self.mark_to_market()

		# submit close order

		self.logger.info(f"Closed Trade {self.current_trade}")

		# add to order book and clean
		self.order_book.append(self.current_trade)
		self.current_trade = Order.empty()

	def forecast_and_size(self):
		forecast, size = 0, 0
		window = self.data_source.get_window()
		self.size_policy.update_datastream(self.data_source)
		if window is not None:
			for trading_rule, forecast_weight in zip(self.trading_rules, self.forecast_weights):
				forecast += forecast_weight * trading_rule.forecast(window)
			size = self.size_policy.position_size(forecast)
		self.logger.info(f"Forcasting {forecast}")
		return forecast, size

	def balance(self):
		return self.accout[-1]["Balance"]

	def get_account_dataframe(self):
		return pd.DataFrame(self.accout)

	def get_account_series(self):
		return self.get_account_dataframe()["Balance"]

	def get_order_book(self):
		orderbook_dict = [order.to_dict() for order in self.order_book]
		return pd.DataFrame(orderbook_dict)

	def mark_to_market(self):
		profit = dict()
		profit["Date"] = self.data_source.get_current_date()
		profit["Balance"] = self.accout[-1]["Balance"]
		open_close_diff = self.data_source.get_current_diff() * self.current_trade.quantity  # * self.leverage
		profit["Balance"] += open_close_diff if self.current_trade.is_position_long() else -open_close_diff
		self.accout.append(profit)

	def simulation_ended(self):
		return self.data_source.limit_reached()

	def trade_next(self):
		"""
		The way this method trades makes it impossible to get out of a bad trade in time,
		turnover rate is usually bad
		Should redefine enter/exit trade methods or even better, write a proper predicat
		component to get more "complex" behaviour
		:return:
		"""

		"""This method trades sequentially one product at a time"""

		if self.simulation_ended():
			return

		forecast, size = self.forecast_and_size()
		self.forecast_history.append({
			"Date": self.data_source.get_current_date(),
			"Forecast": forecast
		})
		self.pose_size_history.append({
			"Date": self.data_source.get_current_date(),
			"PositionSize": size
		})

		if not self.current_trade.is_trade_open() and self.trading_policy.enter_trade_predicat(forecast):
			self.open_trade(forecast, size, self.data_source.get_current_date())

		elif self.current_trade.is_trade_open() and self.trading_policy.exit_trade_predicat(forecast):
			self.close_trade(forecast, self.data_source.get_current_date())

		self.mark_to_market()

		try:
			self.data_source.next()
		except StopIteration:
			pass

	def volatility_normalized_PnL(self):
		account = np.array(self.account_dataframe()["Balance"]) - self.accout[0]["Balance"]
		return account.mean()/account.std()

	def forecast_dataframe(self):
		return pd.DataFrame(self.forecast_history)

	def account_dataframe(self):
		return pd.DataFrame(self.accout)

	def position_dataframe(self):
		return pd.DataFrame(self.pose_size_history)

	def run(self):
		# while not self.simulation_ended():
		for _ in self.data_source:
			self.trade_next()

	def run_tqdm(self):
		# while not self.simulation_ended():
		for _ in tqdm.tqdm(self.data_source):
			self.trade_next()
