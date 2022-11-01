import pandas as pd

from melo_fwk.size_policies import VolTargetSizePolicy
from melo_fwk.size_policies.vol_target import VolTarget

class VolTargetDiscreteSizePolicy(VolTargetSizePolicy):

	def __init__(self, vol_target: VolTarget = VolTarget(0., 0.)):
		super(VolTargetDiscreteSizePolicy, self).__init__(vol_target)

	def position_size_vect(self, forecast: pd.Series, lookback: int = 36) -> pd.Series:
		pose_series = (self.vol_scalar(lookback) * forecast) / 10.
		return pose_series.round()
