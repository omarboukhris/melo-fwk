import numpy as np

import pandas as pd

from melo_fwk.pose_size_vect import VolTargetSizePolicy

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

		# for p in self.product_names():
		# 	pose_inertia_df[p].clip(upper=self.cap_vect[p], lower=-self.cap_vect[p])
		# return pose_inertia_df
		_inertia_vect.i = 0
		return pose_df.apply(_inertia_vect, axis=0)