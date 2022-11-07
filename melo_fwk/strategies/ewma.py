
from melo_fwk.strategies import BaseStrategy

from dataclasses import dataclass

import pandas as pd
import numpy as np

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

	def forecast_vect(self, data: pd.Series):
		fast_ewma = data.ewm(span=int(self.fast_span)).mean()
		slow_ewma = data.ewm(span=int(self.slow_span)).mean()
		std = data.ewm(span=36).std()

		ewma = fast_ewma - slow_ewma

		# np.seterr(invalid="ignore")
		forecast_vect = self.scale * (ewma / std)
		# np.seterr(invalid="warn")
		return forecast_vect
