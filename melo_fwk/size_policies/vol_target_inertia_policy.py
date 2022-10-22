import pandas as pd

from melo_fwk.size_policies import VolTargetSizePolicy
from melo_fwk.size_policies.vol_target import VolTarget

class VolTargetInertiaPolicy(VolTargetSizePolicy):

	def __init__(self, risk_policy: VolTarget = VolTarget(0., 0.), block_size: int = 1):
		super(VolTargetInertiaPolicy, self).__init__(risk_policy, block_size)

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



