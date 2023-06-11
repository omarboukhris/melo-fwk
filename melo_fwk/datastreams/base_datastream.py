
import melo_fwk.datastreams.utils.common as common

import pandas as pd

class BaseDataStream:

	def __init__(
		self,
		dataframe: pd.DataFrame,
		date_label: str = "Date"
	):

		self.dataframe = dataframe.set_index(date_label, drop=False)
		self.date_label = date_label
		self.years = common.parse_year_from_date(self.dataframe)

	def get_dataframe(self):
		""" Get the whole dataframe """
		return self.dataframe

	def get_date_series(self):
		""" Get the whole dataframe """
		return self.dataframe[self.date_label]

	@staticmethod
	def get_empty():
		return BaseDataStream(pd.DataFrame([{"Date": "1970-01-01"}]))

