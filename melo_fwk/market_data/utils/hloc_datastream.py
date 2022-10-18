
import pandas as pd

import datetime as dt

class HLOCDataStream:
	"""This class is used to wrap HLOC Data Frames in a class and to offer some HLOC operations interface"""

	@staticmethod
	def get_empty():
		return HLOCDataStream(
			dataframe=pd.DataFrame([{"Date": "1970-01-01"}])
		)

	def __init__(
		self,
		dataframe: pd.DataFrame,
		offset: int = 0,
		reverse: bool = False,
		date_label: str = "Date"
	):

		self.dataframe = dataframe
		self.offset = offset
		self.reverse = reverse
		self.time_idx = -self.offset if self.reverse else self.offset
		self.date_label = date_label

		self._parse_date_column()
		self._with_daily_returns()

	def _parse_date_column(self):
		def parse_date(date: str):
			try:
				return dt.datetime.strptime(date, "%Y-%m-%d").year
			except ValueError:
				return dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S%z").year
			except Exception as e:
				print(f"HLOCDataStream can't parse date [{date}]")
				raise e

		self.dataframe["Year"] = self.dataframe[self.date_label].apply(parse_date)

	def _with_daily_returns(self):
		self.dataframe["Daily_diff"] = self.dataframe["Close"].diff()

	def get_data_by_year(self, y: str):
		return HLOCDataStream(
			dataframe=self.dataframe.loc[
				self.dataframe["Year"] == y,
			].reset_index(drop=True),
			offset=self.offset,
			reverse=self.reverse,
			date_label=self.date_label,
		)

	def reset(self):
		self.time_idx = -self.offset if self.reverse else self.offset

	def set_offset(self, offset: int):
		self.offset = offset

	def get_data(self):
		""" Get the whole dataframe """
		return self.dataframe

	def get_dates(self):
		""" Get the whole dataframe """
		return self.dataframe["Date"]

	def limit_reached(self):
		return (
			(self.reverse and self.time_idx <= -len(self.dataframe)-1) or
			(not self.reverse and self.time_idx >= len(self.dataframe))
		)

	def get_current_date(self):
		""" Get current Date """
		return self.dataframe.iloc[self.time_idx][self.date_label]

	def get_open(self):
		""" Get current open price """
		return self.dataframe["Open"]

	def get_current_open(self):
		""" Get current open price """
		return self.dataframe.iloc[self.time_idx]["Open"]

	def get_close(self):
		""" Get current close price """
		return self.dataframe["Close"]

	def get_current_close(self):
		""" Get current close price """
		return self.dataframe.iloc[self.time_idx]["Close"]

	def get_close_at_index(self, timestamp: str):
		""" Get closing price at specified timestamp """
		x = self.dataframe.loc[self.dataframe[self.date_label] == timestamp, "Close"].to_numpy()
		assert len(x) == 1, "(AssertionError) Timestamp is invalid, date not found or not unique"
		return x[0]

	def get_daily_diff_vect(self):
		return self.dataframe["Daily_diff"]

	def get_current_diff(self):
		return self.dataframe.iloc[self.time_idx]["Daily_diff"]

	def get_diff_from_index(self, timestamp: str):
		""" Fetch difference between two successive timestamps """
		return self.dataframe.loc[self.dataframe[self.date_label] == timestamp, "Daily_diff"]

	def get_current_high(self):
		return self.dataframe.iloc[self.time_idx]["High"]

	def get_current_low(self):
		return self.dataframe.iloc[self.time_idx]["Low"]

	def get_current_time_index(self):
		return self.time_idx

	def get_window(self, window_size: int = 70):
		if self.reverse and self.time_idx > -len(self.dataframe) + window_size:
			return self.dataframe[self.time_idx - window_size: self.time_idx]
		elif not self.reverse and self.time_idx < len(self.dataframe) - window_size:
			return self.dataframe[self.time_idx: self.time_idx + window_size]
		else:
			return None

	def next(self):
		return self.__next__()

	def __iter__(self):
		return self

	def __next__(self):
		self.time_idx += -1 if self.reverse else 1
		if not self.limit_reached() and self.time_idx in self.dataframe.index:
			try:
				return self.dataframe.iloc[self.time_idx]
			except IndexError as e:
				pass
		else:
			raise StopIteration()
