import numpy as np
import pandas as pd

from melo_fwk.size_policies.vol_target import VolTarget


class BaseSizePolicy:
	def __init__(self, risk_policy: VolTarget = VolTarget(0., 0.), block_size: int = 100):
		self.datastream = None
		self.risk_policy = risk_policy
		self.block_size = block_size

	def update_datastream(self, datastream):
		self.datastream = datastream

	def update_risk_policy(self, risk_policy: VolTarget):
		self.risk_policy = risk_policy

	def position_size_vect(self, forecast: pd.Series) -> pd.Series:
		return pd.Series(np.ones(shape=(len(forecast),)))
