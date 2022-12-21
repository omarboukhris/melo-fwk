from typing import List

import pandas as pd

from melo_fwk.datastreams import TsarDataStream


class ResultsBasket:

	def __init__(self, results_list: List[TsarDataStream]):
		self.results_map = {r.name: r for r in results_list}

	def get_year(self, y: int):
		return ResultsBasket([r.get_year(y) for r in self.results_map.values()])

	def get_product(self, name: str) -> TsarDataStream:
		return self.results_map[name]

	def balance_delta_vect(self) -> pd.Series:
		return pd.Series({
			name: r.balance_delta()
			for name, r in self.results_map.items()
		})

	def years(self):
		return set.intersection(*map(set, [r.years for r in self.results_map.values()]))

	def yearly_balance_sheet(self):
		results = {
			year: self.get_year(year)
			for year in self.years()
		}

		return pd.DataFrame({y: r.balance_delta_vect() for y, r in results.items()})

	"""
	ADD METRICS FROM TSARDATASTREAM
	"""