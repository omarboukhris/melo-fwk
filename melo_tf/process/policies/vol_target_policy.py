
from dataclasses import dataclass
from math import sqrt

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
	def position_size(self, forecast: float) -> float:
		pass

class ConstSizePolicy(ISizePolicy):
	def position_size(self, forecast: float) -> float:
		return 1.0

class VolTargetSizePolicy(ISizePolicy):

	def __init__(self, datastream, risk_policy: VolTarget):
		super(VolTargetSizePolicy, self).__init__()
		self.datastream = datastream
		self.risk_policy = risk_policy

	def price_vol(self, lookback: int = 36) -> float:
		daily_return = self.datastream.get_data()["Daily_diff"]
		ewma_vol = daily_return.ewm(span=lookback).mean().to_numpy()
		current_price = self.datastream.get_close()
		price_vol_vect = ewma_vol * current_price
		if len(price_vol_vect) == 0:
			raise Exception(f"Price volatility vector's size is 0 : {price_vol_vect}")
		return price_vol_vect[-1]

	def block_value(self) -> float:
		return self.datastream.get_close() * 0.01  # * unit_leverage  # = how many shares the contract controls

	def instrument_vol(self) -> float:
		return self.block_value() * self.price_vol()

	def vol_scalar(self) -> float:
		return self.instrument_vol() / self.risk_policy.daily_cash_vol_target()

	def position_size(self, forecast: float) -> float:
		return self.vol_scalar() * forecast / 10.


