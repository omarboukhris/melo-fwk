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
