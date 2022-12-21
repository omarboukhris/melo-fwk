from typing import List

import pandas as pd

from melo_fwk.datastreams import TsarDataStream


class ResultsBasket:

	def __init__(self, results_list: List[TsarDataStream]):
		self.results_list = results_list

	def get_year(self, y: int):
		return ResultsBasket([r.get_year(y) for r in self.results_list])

	def balance_delta_vect(self) -> pd.Series:
		return pd.Series({
			r.name: r.balance_delta()
			for r in self.results_list
		})

	def years(self):
		years = set(self.results_list[0].years)
		for p in self.results_list[1:]:
			years.intersection(p.years)
		return years

	def yearly_balance_sheet(self):
		results = {
			year: self.get_year(year)
			for year in self.years()
		}

		return pd.DataFrame({y: r.balance_delta_vect() for y, r in results.items()})

