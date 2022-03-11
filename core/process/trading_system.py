
import numpy as np
import pandas as pd
import copy

from core.datastreams import DataStream, PandasDataStream

from core.rules import EWMATradingRule

def get_yfinance_dataframe_date(dataframe: pd.DataFrame, time_idx: int):
	return dataframe[time_idx]["Datetime"]

def base_enter_trade_predicat(forcast: float):
	return forcast != 0 and forcast is not None

def base_exit_trade_predicat(forcast: float):
	# if 1 > forcast > -1:
	# 	print(forcast)
	# return forcast == 0
	return -.1 < forcast < .1

class TradingSystem:
	"""Class for backtesting offline a trading system.
	This class trades only one position, one product at a time.
	To backtest for a whole portfolio, you need a TradingSystem/asset,
	then sum up after an iteration.
	Sub-classes can implement multi-threaded execution if needed.

	TODO:
		Implement a TradingSystem class handling multiple positions sequentially
		Implement an OnlineTradingSystem class to handle trades after deployment
		Implement a TradingFramework containing a list of TradingSystem to backtest whole portfolio

	Needs :
	- a data source for historic price data
	- a set of trading rules
	- a set of forcast weights (sum(w_i) == 1)
	- a predicat for entering a trade
	- a predicat for exiting a trade
	"""

	OPEN = True
	CLOSED = False
	EMPTY_TRADE = {
		"status": CLOSED,
		"size": 1.,
		"position": "standby",
		"forcast": [0., 0.],  # (open, close)
		"entry_time": "",
		"exit_time": "",
	}

	def __init__(
		self,
		balance: float,
		data_source: DataStream,
		trading_rules: list,
		forcast_weights: list,
		enter_trade_fn: callable = base_enter_trade_predicat,
		exit_trade_fn: callable = base_exit_trade_predicat):

		assert data_source is not None, "(AssertionError) Data source is None"
		assert len(trading_rules) == len(forcast_weights), \
			"(AssertionError) Number of TradingRules must match forcast weights"

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
		self.forcast_weights = forcast_weights
		self.enter_trade_fn = enter_trade_fn
		self.exit_trade_fn = exit_trade_fn

	def reset(self):
		self.time_index = 0
		self.order_book = []
		self.current_trade = TradingSystem.EMPTY_TRADE

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
		self.current_trade["entry_time"] = entry_time

	def close_trade(self, forcast: float, exit_time: str):
		# update open trade values
		self.current_trade["status"] = TradingSystem.CLOSED
		self.current_trade["forcast"][1] = forcast
		self.current_trade["exit_time"] = exit_time
		self.update_balance()

		# add to order book and clean temporary
		self.order_book.append(copy.deepcopy(self.current_trade))
		# self.order_book.append(self.current_trade)
		self.current_trade = TradingSystem.EMPTY_TRADE

	def forcast(self):
		s = 0
		for trading_rule, forcast_weight in zip(self.trading_rules, self.forcast_weights):
			window = self.data_source.get_window()
			if window is not None:
				s += forcast_weight * trading_rule.forcast(window)
		return s

	def get_account_history(self):
		return pd.DataFrame(self.accout)

	def get_order_book(self):
		return pd.DataFrame(self.order_book)

	def update_balance(self):
		"""update this method to use DataStreams"""
		profit = dict()
		profit["Date"] = self.data_source.get_current_date()
		profit["Balance"] = self.accout[-1]["Balance"]
		if self.is_trade_open(): # mark to market
			profit["Balance"] = self.data_source.get_close_at_index(self.current_trade["entry_time"]) - \
								self.data_source.get_close_at_index(self.data_source.get_current_date())
			profit["Balance"] = profit["Balance"] if self.is_position_long() else -profit["Balance"]
		else:
			profit["Balance"] = self.data_source.get_close_at_index(self.current_trade["entry_time"]) - \
								self.data_source.get_close_at_index(self.current_trade["exit_time"])
			profit["Balance"] = profit["Balance"] if self.is_position_long() else -profit["Balance"]
		self.accout.append(copy.deepcopy(profit))

	def simulation_ended(self):
		return self.data_source.limit_reached()

	def trade_next(self):
		"""This method trades sequentially one product at a time"""

		if self.simulation_ended():
			return

		forcast = self.forcast()

		if not self.is_trade_open() and self.enter_trade_fn(forcast):
			self.open_trade(forcast, self.data_source.get_current_date())
			self.update_balance()  # or mark to marker

		elif self.is_trade_open() and self.exit_trade_fn(forcast):
			self.close_trade(forcast, self.data_source.get_current_date())

		else:
			self.update_balance()  # or mark to marker

		try:
			self.data_source.next()
		except StopIteration:
			pass

	def sharpe_ratio(self):
		account = np.array(self.accout)
		return account.mean()/account.std()


if __name__ == "__main__":
	df = pd.read_csv("data/FB_1d_10y.csv")
	pds = PandasDataStream(df)

	sma_params = {
		"fast_span": 1,
		"slow_span": 8,
		"scaling_factor": 20,
		"cap": 20,
	}
	sma = EWMATradingRule("sma", sma_params)

	tr_sys = TradingSystem(
		balance=0,
		data_source=pds,
		trading_rules=[sma],
		forcast_weights=[1.]
	)

	while not tr_sys.simulation_ended():
		tr_sys.trade_next()

	print(tr_sys.get_account_history(), end="\n\n")
	print(tr_sys.get_order_book())
