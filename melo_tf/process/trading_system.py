
import numpy as np
import pandas as pd
import copy

from melodb.loggers import ILogger
from melodb.Order import Order

from process.policies.trading_policy import BaseTradingPolicy, ITradingPolicy


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

	EMPTY_TRADE = Order.empty()

	component_name = "TradingSystem"

	def __init__(
		self,
		balance: float,
		data_source,
		trading_rules: list,
		forecast_weights: list,
		trading_policy: ITradingPolicy = BaseTradingPolicy(),
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
		self.current_trade = TradingSystem.EMPTY_TRADE
		self.data_source = data_source
		self.trading_rules = trading_rules
		self.forecast_weights = forecast_weights
		self.trading_policy = trading_policy

		self.logger.info(f"Trading System for data source '{self.data_source.name}' initialized")

	def reset(self):
		self.time_index = 0
		self.order_book = []
		self.current_trade = TradingSystem.EMPTY_TRADE

	def is_trade_open(self):
		return self.current_trade.status == Order.Status.OPEN

	def is_position_long(self):
		return self.current_trade.side == Order.Side.LONG

	def is_position_short(self):
		return self.current_trade.side == Order.Side.SHORT

	def open_trade(self, forecast: float, entry_time: str):
		self.current_trade.status = Order.Status.OPEN
		self.current_trade.side = Order.Side.BUY if forecast > 0 else Order.Side.SELL
		self.current_trade.forecast[0] = forecast
		self.current_trade.open_ts = entry_time

		self.logger.info(f"Opened Trade {self.current_trade}")

	def close_trade(self, forecast: float, exit_time: str):
		# update open trade values
		self.current_trade.status = Order.Status.CLOSED
		self.current_trade.forecast[1] = forecast
		self.current_trade.close_ts = exit_time
		self.update_balance()

		self.logger.info(f"Closed Trade {self.current_trade}")

		# add to order book and clean temporary
		self.order_book.append(copy.deepcopy(self.current_trade))
		# self.order_book.append(self.current_trade)
		self.current_trade = TradingSystem.EMPTY_TRADE

	def forecast(self):
		s = 0
		for trading_rule, forecast_weight in zip(self.trading_rules, self.forecast_weights):
			window = self.data_source.get_window()
			if window is not None:
				s += forecast_weight * trading_rule.forecast(window)
		self.logger.info(f"Forcasting {s}")
		return s

	def get_account_history(self):
		return pd.DataFrame(self.accout)

	def get_order_book(self):
		orderbook_dict = [order.to_dict() for order in self.order_book]
		return pd.DataFrame(orderbook_dict)

	def update_balance(self):
		"""
		implemented continous trading
		should rename class to continuous trading system
		"""
		profit = dict()
		profit["Date"] = self.data_source.get_current_date()
		profit["Balance"] = self.accout[-1]["Balance"]
		open_close_diff = self.data_source.get_current_diff()
		profit["Balance"] += open_close_diff if self.is_position_long() else -open_close_diff
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

		forecast = self.forecast()

		if not self.is_trade_open() and self.trading_policy.enter_trade_predicat(forecast):
			self.open_trade(forecast, self.data_source.get_current_date())

		# elif self.trading_policy.turnover_predicat(forecast):
		# 	self.close_trade(forecast, self.data_source.get_current_date())
		# 	self.open_trade(forecast, self.data_source.get_current_date())
		# 	self.update_balance()  # or mark to marker

		elif self.is_trade_open() and self.trading_policy.exit_trade_predicat(forecast):
			self.close_trade(forecast, self.data_source.get_current_date())

		self.update_balance()  # or mark to market

		try:
			self.data_source.next()
		except StopIteration:
			pass

	def sharpe_ratio(self):
		account = np.array(pd.DataFrame(self.accout)["Balance"])
		return account.mean()/account.std()

		# diff_mean = account.mean() - self.data_source.get_data()["Close"].mean()
		# diff_std = account.std() - self.data_source.get_data()["Close"].std()
		# return diff_mean / diff_std

	def run(self):
		while not self.simulation_ended():
			self.trade_next()
