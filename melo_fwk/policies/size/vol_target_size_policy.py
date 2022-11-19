import pandas as pd

from melo_fwk.policies.size.base_size_policy import BaseSizePolicy

class VolTargetSizePolicy(BaseSizePolicy):

	def __init__(
		self,
		annual_vol_target: float,
		trading_capital: float
	):
		super(VolTargetSizePolicy, self).__init__(
			annual_vol_target, trading_capital
		)

	def price_vol(self, lookback: int = 36) -> pd.Series:
		daily_return = self.datastream.get_daily_diff_series()
		ewma_vol = daily_return.ewm(span=lookback).std()
		close_mean = self.datastream.get_close_series().ewm(span=lookback).mean()

		price_vol_vect = ewma_vol / close_mean
		return price_vol_vect

	def block_value(self, lookback: int = 36) -> pd.Series:
		# 1% price differencial
		return self.datastream.get_close_series().ewm(span=lookback).mean() * self.block_size
		# block_size = how many shares the contract controls

	def instrument_vol(self, lookback: int = 36) -> pd.Series:
		return self.block_value(lookback) * self.price_vol(lookback)

	def vol_scalar(self, lookback: int = 36) -> pd.Series:
		# return self.instrument_vol(lookback) / self.vol_target.daily_cash_vol_target()
		return self.vol_target.daily_cash_vol_target() / self.instrument_vol(lookback)

	def position_size(self, forecast: float, lookback: int = 36) -> float:
		return self.vol_scalar(lookback).iat[-1] * forecast / 10.

	def position_size_vect(self, forecast: pd.Series, lookback: int = 36) -> pd.Series:
		# mean (forecast) = 10 // forecast / 10 == buy and hold € [-2, 2]
		return (self.vol_scalar(lookback) * forecast) / 10.


