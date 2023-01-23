from typing import List

import numpy as np
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

	def apply_weights(self, weights):
		weighted_results = []
		for w, result in zip(weights, self.results_map.values()):
			weighted_results.append(result.apply_weight(w))
		return ResultsBasket(weighted_results)

	def accumulate(self, column: str):
		acc = {}
		for k, tsar in self.results_map.items():
			acc[k] = tsar.dataframe[column]
		return pd.DataFrame(acc).dropna().sum(axis=1)

	def rolling(self, column: str):
		rolling_result = {}
		for prod_name, tsar in self.results_map.items():
			rolling_result[prod_name] = [
				roll_tsar[column].reset_index(drop=True)
				for roll_tsar in tsar.rolling_dataframe()
			]
		min_len = min([len(r) for r in rolling_result.values()])
		trim_rolling_result = {
			prod: r[:min_len] for prod, r in rolling_result.items()
		}

		# transpose dict to list of dataframes
		out = [
			pd.DataFrame({
				k: trim_rolling_result[k][i]
				for k in trim_rolling_result.keys()
			})
			for i in range(min_len)
		]

		return out


	"""
	TODO: ADD METRICS FROM TSARDATASTREAM
	"""