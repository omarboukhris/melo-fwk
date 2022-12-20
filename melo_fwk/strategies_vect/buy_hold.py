
from melo_fwk.strategies_vect import BaseStrategy

from dataclasses import dataclass

import pandas as pd
import numpy as np

@dataclass
class BuyAndHold(BaseStrategy):

	def forecast_vect(self, data: pd.DataFrame) -> pd.Series:
		# const forecast of 10 for proper vol targeting
		return 10 * pd.DataFrame(np.ones(shape=data.shape))

