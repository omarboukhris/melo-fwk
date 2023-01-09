import numpy as np

import pandas as pd

from melo_fwk.pose_size import VolTargetSizePolicy

class VolTargetInertiaPolicy(VolTargetSizePolicy):

	def __init__(
		self,
		annual_vol_target: float,
		trading_capital: float
	):
		super(VolTargetInertiaPolicy, self).__init__(
			annual_vol_target, trading_capital
		)

	def position_size_df(self, forecast: pd.Series, lookback: int = 36) -> pd.DataFrame:
		def _inertia_vect(pose: pd.Series) -> pd.Series:
			_inertia_vect.i += 1
			_inertia.curr_pose = 0
			return pose.apply(_inertia).round().clip(
				upper=self.cap_vect[_inertia_vect.i-1],
				lower=-self.cap_vect[_inertia_vect.i-1]
			)

		def _inertia(pose: float) -> float:
			pose_diff = abs(pose - _inertia.curr_pose)
			thr = _inertia.curr_pose * 0.1
			if pose_diff > thr:
				_inertia.curr_pose = pose
			return _inertia.curr_pose

		pose_df = (self.vol_vect(lookback) * forecast) / 10.

		_inertia_vect.i = 0
		return pose_df.apply(_inertia_vect, axis=0)


	def position_size_vect(self, forecast: pd.Series, lookback: int = 36) -> pd.Series:
		def _inertia(pose: float) -> float:
			pose_diff = abs(pose - _inertia.curr_pose)
			thr = _inertia.curr_pose * 0.1
			if pose_diff > thr:
				_inertia.curr_pose = pose
			return _inertia.curr_pose

		_inertia.curr_pose = 0
		pose_series = pd.Series((self.vol_scalar(lookback) * forecast.to_numpy()) / 10.)
		return pose_series.apply(_inertia).round().clip(upper=self.cap, lower=-self.cap)

