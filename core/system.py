
import numpy as np

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

	def __init__(
		self,
		balance: float,
		data_source: dict,
		trading_rules: list,
		forcast_weights: list,
		enter_trade_fn: callable,
		exit_trade_fn: callable):

		self.accout = [balance]
		self.current_trade = {
			"ongoing": False,
			"position": 0,
			"entry_ts": 0,
			"exit_ts": 0,
		}
		self.data_source = data_source
		self.trading_rules = trading_rules
		self.forcast_weights = forcast_weights
		self.enter_trade_fn = enter_trade_fn
		self.exit_trade_fn = exit_trade_fn

	def forcast(self):
		s = 0
		for trading_rule, forcast_weight in zip(self.trading_rules, self.forcast_weights):
			s += forcast_weight * trading_rule.forcast(self.data_source)
		return s

	def update_balance(self):
		profit = self.data_source[self.current_trade["entry_ts"]] - self.data_source[self.current_trade["exit_ts"]]
		profit = profit if self.current_trade["position"] > 0 else -profit
		self.accout.append(profit)

	def trade(self):
		"""This method trades sequentially one product at a time"""

		if self.data_source is None:
			return

		for i in range(len(self.data_source)):
			forcast = self.forcast()
			if not self.current_trade["ongoing"] and self.enter_trade_fn(forcast):
				self.current_trade["ongoing"] = True
				self.current_trade["position"] = forcast
				self.current_trade["entry_ts"] = i
			elif self.current_trade["ongoing"] and self.exit_trade_fn(forcast):
				self.current_trade["ongoing"] = False
				self.current_trade["exit_ts"] = i
				self.update_balance()

	def sharpe_ratio(self):
		account = np.array(self.accout)
		return account.mean()/account.std()
