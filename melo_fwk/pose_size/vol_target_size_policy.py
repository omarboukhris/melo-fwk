import pandas as pd
import numpy as np

from melo_fwk.pose_size.base_size_policy import BaseSizePolicy

class VolTargetSizePolicy(BaseSizePolicy):

	def __init__(
		self,
		annual_vol_target: float,
		trading_capital: float
	):
		super(VolTargetSizePolicy, self).__init__(
			annual_vol_target, trading_capital
		)

	# ======= Basket Processing
	def price_vol_vect(self, lookback: int = 36) -> pd.DataFrame:
		ewma_vol = self.prod_basket.daily_diff_df().ewm(span=lookback, axis=0).std()
		close_mean = self.prod_basket.close_df().ewm(span=lookback, axis=0).mean()

		price_vol_df = ewma_vol / close_mean
		return price_vol_df

	def block_value_vect(self, lookback: int = 36) -> pd.DataFrame:
		# 1% price differencial
		return pd.DataFrame(
			np.einsum(
				"i,ji->ji",
				self.block_size_vect.to_numpy(),
				self.prod_basket.close_df().ewm(span=lookback, axis=0).mean().to_numpy()),
			columns=self.product_names()
		)
		# block_size = how many shares the contract controls

	def instrument_vol_vect(self, lookback: int = 36) -> pd.DataFrame:
		return self.block_value_vect(lookback) * self.price_vol_vect(lookback)

	def vol_vect(self, lookback: int = 36) -> pd.DataFrame:
		# return self.instrument_vol(lookback) / self.vol_target.daily_cash_vol_target()
		return self.vol_target.daily_cash_vol_target() / self.instrument_vol_vect(lookback)

	def position_size_df(self, forecast: pd.DataFrame, lookback: int = 36) -> pd.DataFrame:
		# mean (forecast) = 10 // forecast / 10 == buy and hold € [-2, 2]
		return (self.vol_vect(lookback) * forecast) / 10.

	# ======= Single Product Processing

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

	def position_size_vect(self, forecast: pd.Series, lookback: int = 36) -> pd.Series:
		# mean (forecast) = 10 // forecast / 10 == buy and hold € [-2, 2]
		return (self.vol_scalar(lookback) * forecast) / 10.
