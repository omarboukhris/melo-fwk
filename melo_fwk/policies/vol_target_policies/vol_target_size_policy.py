import pandas as pd

from melo_fwk.policies.vol_target_policies.base_size_policy import ISizePolicy
from melo_fwk.policies.vol_target_policies.vol_target import VolTarget

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


