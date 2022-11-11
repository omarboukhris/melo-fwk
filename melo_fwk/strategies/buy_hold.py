


from melo_fwk.strategies import BaseStrategy

from dataclasses import dataclass

import pandas as pd
import numpy as np

@dataclass
class BuyAndHold(BaseStrategy):

	def forecast_vect(self, data: pd.Series) -> pd.Series:
		return pd.Series(np.ones(shape=(len(data),)))
