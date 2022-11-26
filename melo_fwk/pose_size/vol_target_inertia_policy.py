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

	def position_size_vect(self, forecast: pd.Series, lookback: int = 36) -> pd.Series:
		def _inertia(pose: float) -> float:
			pose_diff = pose - _inertia.curr_pose
			thr = _inertia.curr_pose * 0.1
			if (pose_diff > 0 and pose_diff > thr) or (pose_diff < 0 and pose_diff < thr):
				_inertia.curr_pose = pose
			return _inertia.curr_pose

		_inertia.curr_pose = 0
		pose_series = (self.vol_scalar(lookback) * forecast) / 10.
		return pose_series.apply(_inertia).round()

