
from minimelo.strategies import BaseStrategy

from dataclasses import dataclass

import pandas as pd


@dataclass
class EWMAParamSpace:
	fast_span: int
	slow_span: int

	search_space = {
		"fast_span": [i for i in range(4, 60)],
		"slow_span": [i for i in range(30, 100)],
	}

@dataclass
class EWMAStrategy(BaseStrategy, EWMAParamSpace):

	def to_dict(self):
		return {
			"cap": self.cap,
			"fast_span": self.fast_span,
			"slow_span": self.slow_span,
			"scale": self.scale
		}

	@staticmethod
	def from_dict(config: dict):
		return EWMAStrategy(**config)

	def forecast_vect(self, data: pd.Series):
		fast_ewma = data.ewm(span=int(self.fast_span), adjust=False).mean()
		slow_ewma = data.ewm(span=int(self.slow_span), adjust=False).mean()

		std = data.ewm(span=36, adjust=False).std()
		ewma = fast_ewma - slow_ewma

		forecast_vect = self.scale * (ewma / std)
		return forecast_vect
