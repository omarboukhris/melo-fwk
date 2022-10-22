import pandas as pd

from melo_fwk.size_policies import (
	VolTarget,
	VolTargetSizePolicy
)

class VolTargetDiscreteSizePolicy(VolTargetSizePolicy):

	def __init__(self, risk_policy: VolTarget = VolTarget(0., 0.), block_size: int = 1):
		super(VolTargetDiscreteSizePolicy, self).__init__(risk_policy, block_size)

	def position_size_vect(self, forecast: pd.Series, lookback: int = 36) -> pd.Series:
		pose_series = (self.vol_scalar(lookback) * forecast) / 10.
		return pose_series.round()
