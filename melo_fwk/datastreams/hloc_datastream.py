import numpy as np
import pandas as pd

from melo_fwk.datastreams.base_datastream import BaseDataStream

import melo_fwk.datastreams.utils.common as common


class HLOCDataStream(BaseDataStream):
	"""This class is used to wrap HLOC Data Frames in an interface and to offer some HLOC operations"""

	def __init__(self, **kwargs):
		super(HLOCDataStream, self).__init__(**kwargs)
		self.dataframe = common.get_daily_diff_from_value(self.dataframe)

	def get_year(self, y: int, stitch: bool = True):
		if stitch:
			return HLOCDataStream(
				dataframe=self.dataframe.loc[
					self.dataframe["Year"].isin([y, y-1])
					].reset_index(drop=True),
				date_label=self._date_label,
			)
		else:
			return HLOCDataStream(
				dataframe=self.dataframe.loc[
					self.dataframe["Year"] == y
					].reset_index(drop=True),
				date_label=self._date_label,
			)

	def get_close_series(self) -> pd.Series:
		""" Get daily close price """
		return self.dataframe["Close"]

	def get_close_at_date(self, date: str) -> float:
		""" Get closing price at specified date """
		return self._get_value_at_date("Close", date)

	def get_open_series(self) -> pd.Series:
		""" Get daily open price """
		return self.dataframe["Open"]

	def get_open_at_date(self, date: str) -> float:
		""" Get open price at date """
		return self._get_value_at_date("Open", date)

	def get_daily_diff_series(self) -> pd.Series:
		return self.dataframe["Daily_diff"]

	def get_diff_at_date(self, date: str) -> float:
		""" Fetch difference between two successive timestamps """
		return self._get_value_at_date("Daily_diff", date)

	def get_high_series(self) -> pd.Series:
		""" Get daily high price """
		return self.dataframe["High"]

	def get_high_at_date(self, date: str) -> float:
		""" Get High price at specified date """
		return self._get_value_at_date("High", date)

	def get_low_series(self) -> pd.Series:
		""" Get daily low price """
		return self.dataframe["Low"]

	def get_low_at_date(self, date: str) -> float:
		""" Get low price at specified date """
		return self._get_value_at_date("Low", date)

	def _get_value_at_date(self, value: str, date: str) -> float:
		x = self.dataframe.loc[self.dataframe[self._date_label] == date, value].to_numpy()
		assert len(x) == 1, "(HLOCDataStream) Timestamp is invalid, date not found or not unique"
		return x[0]
