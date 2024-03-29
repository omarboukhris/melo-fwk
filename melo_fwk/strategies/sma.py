
from melo_fwk.strategies import BaseStrategy

from dataclasses import dataclass

import pandas as pd


@dataclass
class SMAParamSpace:
	fast_span: int
	slow_span: int

	search_space = {
		"fast_span": [i for i in range(4, 60)],
		"slow_span": [i for i in range(30, 100)],
	}

@dataclass
class SMAStrategy(BaseStrategy, SMAParamSpace):

	def to_dict(self):
		return {
			"cap": self.cap,
			"fast_span": self.fast_span,
			"slow_span": self.slow_span,
			"scale": self.scale
		}

	@staticmethod
	def from_dict(config: dict):
		return SMAStrategy(**config)

	def forecast_df(self, data: pd.DataFrame) -> pd.DataFrame:
		fast_sma = data.rolling(int(self.fast_span), min_periods=1, axis=1).mean()
		slow_sma = data.rolling(int(self.slow_span), min_periods=1, axis=1).mean()

		std = data.rolling(25, min_periods=1, axis=1).std()
		sma = fast_sma - slow_sma

		forecast_vect = self.scale * (sma / std)
		return forecast_vect

	def forecast_vect(self, data: pd.Series) -> pd.Series:
		fast_sma = data.rolling(int(self.fast_span), min_periods=1).mean()
		slow_sma = data.rolling(int(self.slow_span), min_periods=1).mean()

		std = data.rolling(25).std()
		sma = fast_sma - slow_sma

		forecast_vect = self.scale * (sma / std)
		return forecast_vect



