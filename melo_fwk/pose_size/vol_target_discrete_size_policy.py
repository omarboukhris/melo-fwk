import pandas as pd

from melo_fwk.pose_size import VolTargetSizePolicy

class VolTargetDiscreteSizePolicy(VolTargetSizePolicy):

	def __init__(
		self,
		annual_vol_target: float,
		trading_capital: float
	):
		super(VolTargetDiscreteSizePolicy, self).__init__(
			annual_vol_target, trading_capital
		)

	def position_size_df(self, forecast: pd.DataFrame, lookback: int = 36) -> pd.DataFrame:
		pose_series = (self.vol_vect(lookback) * forecast) / 10.
		return pose_series.round()

	def position_size_vect(self, forecast: pd.Series, lookback: int = 36) -> pd.Series:
		pose_series = (self.vol_scalar(lookback) * forecast) / 10.
		return pose_series.round()
