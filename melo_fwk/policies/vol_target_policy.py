
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

	def __init__(self, risk_policy: VolTarget = VolTarget(0., 0.), unit_leverage: int = 100):
		super(VolTargetSizePolicy, self).__init__(risk_policy)
		self.unit_leverage = unit_leverage

	def price_vol(self, lookback: int = 36) -> pd.Series:
		daily_return = self.datastream.get_daily_diff_vect()
		# ewma_vol = daily_return.ewm(span=lookback).std()
		close_vect = self.datastream.get_close()

		# price_vol_vect = ewma_vol * current_price
		price_vol_vect = daily_return * close_vect
		return price_vol_vect

	def block_value(self) -> pd.Series:
		return self.datastream.get_close() * 0.01 * self.unit_leverage  # = how many shares the contract controls

	def instrument_vol(self) -> pd.Series:
		return self.block_value() * self.price_vol()

	def vol_scalar(self) -> pd.Series:
		return self.instrument_vol() / self.risk_policy.daily_cash_vol_target()

	def position_size(self, forecast: float) -> float:
		return self.vol_scalar().iat[-1] * forecast / 10.

	def position_size_vect(self, forecast: pd.Series) -> pd.Series:
		return self.vol_scalar() * forecast / 10.


