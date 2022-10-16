import pandas as pd

from melo_fwk.policies.vol_target_policies.vol_target import VolTarget


class ISizePolicy:
	def __init__(self, risk_policy: VolTarget = VolTarget(0., 0.)):
		self.datastream = None
		self.risk_policy = risk_policy

	def update_datastream(self, datastream):
		self.datastream = datastream

	def position_size(self, forecast: float) -> float:
		pass

	def position_size_vect(self, forecast: pd.Series) -> pd.Series:
		pass


class ConstSizePolicy(ISizePolicy):
	def __init__(self, risk_policy: VolTarget = VolTarget(0., 0.)):
		super(ConstSizePolicy, self).__init__(risk_policy)

	def position_size(self, forecast: float) -> float:
		return forecast/abs(forecast) if forecast != 0 else 0

	def position_size_vect(self, forecast: pd.Series) -> pd.Series:
		return forecast/forecast.abs()
