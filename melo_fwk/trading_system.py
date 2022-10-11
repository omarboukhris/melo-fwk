
import pandas as pd
import tqdm

from melodb.loggers import ILogger
from melodb.Order import Order

from melo_fwk.datastreams.datastream import HLOCDataStream
from melo_fwk.policies.trading_policy import BaseTradingPolicy, ITradingPolicy
from melo_fwk.policies.vol_target_policy import ConstSizePolicy, ISizePolicy, VolTarget
from melo_fwk.metrics.metrics import AccountMetrics

from dataclasses import dataclass

@dataclass(frozen=True)
class TradingSystemAnnualResult:
	account_metrics: AccountMetrics
	forecast_df: pd.DataFrame
	size_df: pd.DataFrame
	account_df: pd.DataFrame
	vol_target: VolTarget

	def annual_delta(self):
		assert len(self.account_df) > 1, \
			"(TradingSystemAnnualReport) final_balance: account data frame is empty"
		return self.account_df.iloc[-1]["Balance"]

class TradingSystem:
	"""Class for backtesting offline a trading system.
	This class trades only one position, one product at a time.
	To backtest for a whole portfolio, you need a TradingSystem per asset,
	then sum up after each iteration.
	Sub-classes can implement multi-threaded execution if needed.

	Needs :
	- a data source for historic price data
	- a set of trading rules
	- a set of forcast weights (sum(w_i) == 1)
	- a policy for entering/exiting trades
	"""

	component_name = "TradingSystem"

	def __init__(
		self,
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
				"Balance": 0,
			}
		]
		self.time_index = 0
		self.order_book = []
		self.positions_history = []
		self.current_trade = Order.empty()
		self.data_source = data_source
		self.trading_rules = trading_rules
		self.forecast_weights = forecast_weights
		self.size_policy = size_policy
		self.trading_policy = trading_policy

	@staticmethod
	def default():
		return TradingSystem(
			data_source=HLOCDataStream.get_empty(),
			trading_rules=[],
			forecast_weights=[]
		)

	def open_trade(self, forecast: float, size: float, entry_time: str):
		# adjust vol target and update size policy object ?
		self.current_trade.open_trade(forecast, abs(size), entry_time)

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
		""" Run a trading iteration :
			- Compute forecast and size
			- Check trade entry & exit conditions
			- Mark to Market
		"""

		if self.simulation_ended():
			return

		forecast, size = self.forecast_and_size()
		self.positions_history.append({
			"Date": self.data_source.get_current_date(),
			"Forecast": forecast,
			"PositionSize": size,
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

	def run(self):
		# while not self.simulation_ended():
		for _ in self.data_source:
			self.trade_next()

	def run_tqdm(self):
		# while not self.simulation_ended():
		for _ in tqdm.tqdm(self.data_source):
			self.trade_next()


	def order_book_dataframe(self):
		orderbook_dict = [order.to_dict() for order in self.order_book]
		return pd.DataFrame(orderbook_dict)

	def forecast_dataframe(self):
		return pd.DataFrame(self.positions_history)[["Date", "Forecast"]]

	def account_dataframe(self):
		return pd.DataFrame(self.accout)

	def account_series(self):
		return pd.DataFrame(self.accout)["Balance"]

	def position_dataframe(self):
		return pd.DataFrame(self.positions_history)[["Date", "PositionSize"]]

	def get_tsar(self):
		return TradingSystemAnnualResult(
			vol_target=self.size_policy.risk_policy,
			account_metrics=AccountMetrics(self.account_series()),
			forecast_df=self.forecast_dataframe(),
			size_df=self.position_dataframe(),
			account_df=self.account_dataframe()
		)
