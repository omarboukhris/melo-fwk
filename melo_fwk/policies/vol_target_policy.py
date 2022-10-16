
from dataclasses import dataclass
from math import sqrt

import pandas as pd


@dataclass(frozen=True)
class VolTarget:
	yearly_trading_days = 256
	annual_vol_target: float
	trading_capital: float

	def annual_cash_vol_target(self):
		return self.annual_vol_target * self.trading_capital

	def daily_cash_vol_target(self):
		return self.annual_cash_vol_target()/sqrt(VolTarget.yearly_trading_days)

	def __str__(self):
		return f"annual vol target : {self.annual_vol_target}\n" +\
			f"trading capital : {self.trading_capital}\n" +\
			f"annual cash vol target : {self.annual_cash_vol_target()}\n" +\
			f"daily cash vol target : {self.daily_cash_vol_target()}\n"


class ISizePolicy:
	def __init__(self, risk_policy: VolTarget = VolTarget(0., 0.)):
		self.datastream = None
		self.risk_policy = risk_policy

	def update_datastream(self, datastream):
		self.datastream = datastream

	def position_size(self, forecast: float) -> float:
		pass

	def position_size_vect(self, forecast: pd.Series) -> pd.Series:
		pass

class ConstSizePolicy(ISizePolicy):
	def __init__(self, risk_policy: VolTarget = VolTarget(0., 0.)):
		super(ConstSizePolicy, self).__init__(risk_policy)

	def position_size(self, forecast: float) -> float:
		return forecast/abs(forecast) if forecast != 0 else 0

	def position_size_vect(self, forecast: pd.Series) -> pd.Series:
		raise NotImplementedError()

class VolTargetSizePolicy(ISizePolicy):

	def __init__(self, risk_policy: VolTarget = VolTarget(0., 0.), block_size: int = 100):
		super(VolTargetSizePolicy, self).__init__(risk_policy)
		self.block_size = block_size

	def price_vol(self, lookback: int = 36) -> pd.Series:
		daily_return = self.datastream.get_daily_diff_vect()
		ewma_vol = daily_return.ewm(span=lookback).std()
		close_mean = self.datastream.get_close().ewm(span=lookback).mean()

		price_vol_vect = ewma_vol / close_mean
		return price_vol_vect

	def block_value(self, lookback: int = 36) -> pd.Series:
		# 1% price differencial
		return self.datastream.get_close().ewm(span=lookback).mean() * self.block_size
		# block_size = how many shares the contract controls

	def instrument_vol(self, lookback: int = 36) -> pd.Series:
		return self.block_value(lookback) * self.price_vol(lookback)

	def vol_scalar(self, lookback: int = 36) -> pd.Series:
		# return self.instrument_vol(lookback) / self.risk_policy.daily_cash_vol_target()
		return self.risk_policy.daily_cash_vol_target() / self.instrument_vol(lookback)

	def position_size(self, forecast: float, lookback: int = 36) -> float:
		return self.vol_scalar(lookback).iat[-1] * forecast / 10.

	def position_size_vect(self, forecast: pd.Series, lookback: int = 36) -> pd.Series:
		return (self.vol_scalar(lookback) * forecast) / 10.


