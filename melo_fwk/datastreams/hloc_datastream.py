
import pandas as pd

from melo_fwk.datastreams.base_datastream import BaseDataStream

import melo_fwk.datastreams.utils.common as common


class HLOCDataStream(BaseDataStream):
	"""This class is used to wrap HLOC Data Frames in an interface and to offer some HLOC operations"""


	def __init__(self, **kwargs):
		super(HLOCDataStream, self).__init__(**kwargs)
		self.dataframe = common.get_daily_diff_from_value(self.dataframe)

	def get_data_by_year(self, y: str):
		return HLOCDataStream(
			dataframe=self.dataframe.loc[
				self.dataframe["Year"] == y,
			].reset_index(drop=True),
			date_label=self._date_label,
		)

	def get_close_series(self) -> pd.Series:
		""" Get current close price """
		return self.dataframe["Close"]

	def get_close_at_date(self, date: str) -> float:
		""" Get closing price at specified date """
		return self._get_value_at_date("Close", date)

	def get_open_series(self) -> pd.Series:
		""" Get current open price """
		return self.dataframe["Open"]

	def get_open_at_date(self, date: str) -> float:
		""" Get current open price """
		return self._get_value_at_date("Open", date)

	def get_daily_diff_series(self) -> pd.Series:
		return self.dataframe["Daily_diff"]

	def get_diff_at_date(self, date: str) -> float:
		""" Fetch difference between two successive timestamps """
		return self._get_value_at_date("Daily_diff", date)

	def _get_value_at_date(self, value: str, date: str) -> float:
		x = self.dataframe.loc[self.dataframe[self._date_label] == date, value].to_numpy()
		assert len(x) == 1, "(AssertionError) Timestamp is invalid, date not found or not unique"
		return x[0]
