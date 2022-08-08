from dataclasses import dataclass
from math import sqrt

class IRiskPolicy:
	pass

@dataclass(frozen=True)
class VolTarget(IRiskPolicy):
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

class VaR:

	def __init__(self):
		pass


if __name__ == "__main__":

	vol_target = VolTarget(0.5, 10000)
	print(vol_target)
