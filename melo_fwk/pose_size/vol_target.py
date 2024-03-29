from dataclasses import dataclass
# from math import sqrt


@dataclass
class VolTarget:
	annual_vol_target: float  # between [0, 1]
	trading_capital: float

	def annual_cash_vol_target(self):
		return self.annual_vol_target * self.trading_capital

	def daily_cash_vol_target(self):
		# yearly_trading_days = 256 => sqrt = 16
		return self.annual_cash_vol_target()/16.

	def to_list(self):
		return self.__str__().split("\n")[:-1]

	def to_dict(self):
		return {
			"annual_vol_target": self.annual_vol_target,
			"trading_capital": self.trading_capital
		}

	def __str__(self):
		return f"Annual vol target : {self.annual_vol_target}\n" +\
			f"Trading capital : {self.trading_capital}\n" +\
			f"Annual cash vol target : {self.annual_cash_vol_target()}\n" +\
			f"Daily cash vol target : {self.daily_cash_vol_target()}\n"
