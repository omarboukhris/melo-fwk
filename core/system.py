
import numpy as np
import pandas as pd


def get_yfinance_dataframe_date(dataframe: pd.DataFrame, time_idx: int):
	return dataframe[time_idx]["Datetime"]

def base_enter_trade_predicat(forcast: float):
	return forcast != 0

def base_exit_trade_predicat(forcast: float):
	return forcast == 0

class TradingSystem:
	"""Class for backtesting offline a trading system.
	This class trades only one position, one product at a time
	Sub-classes can implement multi-threaded execution.

	TODO: Implement a TradingSystem class handling multiple positions sequentially

	Needs :
	- a data source for historic price data
	- a set of trading rules
	- a set of forcast weights (sum(w_i) == 1)
	- a predicat for entering a trade
	- a predicat for exiting a trade
	"""

	OPEN = True
	CLOSED = False

	def __init__(
		self,
		balance: float,
		data_source: pd.DataFrame,
		trading_rules: list,
		forcast_weights: list,
		date_parser_fn: callable = get_yfinance_dataframe_date,
		enter_trade_fn: callable = base_enter_trade_predicat,
		exit_trade_fn: callable = base_exit_trade_predicat):

		self.accout = [balance]
		self.order_book = []
		self.current_trade = {
			"status": TradingSystem.CLOSED,
			"size": 1.,
			"position": "standby",
			"forcast": [0., 0.],  # (open, close)
			"entry_time": "",
			"exit_time": "",
		}
		self.data_source = data_source
		self.trading_rules = trading_rules
		self.forcast_weights = forcast_weights
		self.date_parser_fn = date_parser_fn
		self.enter_trade_fn = enter_trade_fn
		self.exit_trade_fn = exit_trade_fn

	def is_trade_open(self):
		return self.current_trade["status"] == TradingSystem.OPEN

	def is_position_long(self):
		return self.current_trade["position"] == "long"

	def is_position_short(self):
		return self.current_trade["position"] == "short"

	def open_trade(self, forcast: float, entry_time: str):
		self.current_trade["status"] = TradingSystem.OPEN
		self.current_trade["position"] = "long" if forcast > 0 else "short"
		self.current_trade["forcast"][0] = forcast
		self.current_trade["entry_ts"] = entry_time

	def close_trade(self, forcast: float, exit_time: str):
		self.current_trade["status"] = TradingSystem.CLOSED
		self.current_trade["forcast"][1] = forcast
		self.current_trade["exit_time"] = exit_time

	def forcast(self):
		s = 0
		for trading_rule, forcast_weight in zip(self.trading_rules, self.forcast_weights):
			s += forcast_weight * trading_rule.forcast(self.data_source)
		return s

	def update_balance(self):
		profit = self.data_source[self.current_trade["entry_time"]] - self.data_source[self.current_trade["exit_time"]]
		profit = profit if self.is_position_long() else -profit
		self.accout.append(profit)

	def trade(self):
		"""This method trades sequentially one product at a time"""

		if self.data_source is None:
			return

		for i in range(len(self.data_source)):
			forcast = self.forcast()

			if not self.is_trade_open() and self.enter_trade_fn(forcast):
				self.open_trade(forcast, self.date_parser_fn(self.data_source, i))

			elif self.is_trade_open() and self.exit_trade_fn(forcast):
				self.close_trade(forcast, self.date_parser_fn(self.data_source, i))

			self.update_balance()  # or mark to marker

	def sharpe_ratio(self):
		account = np.array(self.accout)
		return account.mean()/account.std()
