
import tqdm
import pandas as pd

from melodb.Order import Order
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem

class TradingSystem(BaseTradingSystem):
	"""Class for backtesting offline a trading system.
	This class trades only one position, one product at a time.
	To backtest for a whole portfolio, you need a TradingSystem per asset,
	then sum up after each iteration.
	Sub-classes can implement multi-threaded execution if needed.

	Needs :
	- a data source for historic price data
	- a set of trading rules
	- a set of forcast weights (sum(w_i) == 1)
	- a pose sizing policy
	- a policy for entering/exiting trades
	"""

	component_name = "TradingSystem"

	def __init__(self, **kwargs):
		super(TradingSystem, self).__init__(**kwargs)
		self.tsar_history = [{
			"Date": self.data_source.get_current_date(),
			"Price": self.data_source.get_close(),
			"Forecast": 0.,
			"PositionSize": 0.,
			"Daily_PnL": 0.,
		}]

	def open_trade(self, forecast: float, size: float, entry_time: str):
		# adjust vol target and update size policy object ?
		self.current_trade.open_trade(forecast, abs(size), entry_time)

		# submit open order

		self.logger.info(f"Opened Trade {self.current_trade}")

	def close_trade(self, forecast: float, exit_time: str):
		self.current_trade.close_trade(forecast, exit_time)

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

	def get_daily_pnl(self):
		open_close_diff = self.data_source.get_current_diff() * self.current_trade.quantity  # * self.leverage
		daily_pnl = open_close_diff if self.current_trade.is_position_long() else -open_close_diff
		return daily_pnl

	def simulation_ended(self):
		return self.data_source.limit_reached()

	def trade_next(self):
		""" Run a trading iteration :
			- Compute forecast and size
			- Check trade entry & exit conditions
			- Mark to Market
		"""

		if self.simulation_ended():
			return

		forecast, size = self.forecast_and_size()

		if not self.current_trade.is_trade_open() and self.trading_policy.enter_trade_predicat(forecast):
			self.open_trade(forecast, size, self.data_source.get_current_date())

		elif self.current_trade.is_trade_open() and self.trading_policy.exit_trade_predicat(forecast):
			self.close_trade(forecast, self.data_source.get_current_date())

		self.tsar_history.append({
			"Date": self.data_source.get_current_date(),
			"Price": self.data_source.get_close(),
			"Forecast": forecast,
			"PositionSize": size,
			"Daily_PnL": self.get_daily_pnl()
		})

		try:
			self.data_source.next()
		except StopIteration:
			pass

	def run(self):
		# while not self.simulation_ended():
		for _ in self.data_source:
			self.trade_next()

	def run_tqdm(self):
		# while not self.simulation_ended():
		for _ in tqdm.tqdm(self.data_source):
			self.trade_next()
