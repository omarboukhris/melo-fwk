
import pandas as pd

import datetime as dt

class DataStream:
	def __init__(self, name: str):
		self.name = name

	def get_data(self) -> pd.DataFrame:
		pass

	def with_daily_returns(self):
		pass

	def get_current_date(self):
		pass

	def get_open(self):
		pass

	def get_close(self):
		pass

	def get_close_at_index(self, timestamp: str):
		pass

	def get_current_diff(self):
		pass

	def get_diff_from_index(self, timestamp: str):
		pass

	def get_high(self):
		pass

	def get_low(self):
		pass

	def get_current_time_index(self):
		pass

	def get_window(self):
		pass

	def limit_reached(self):
		pass

	def next(self):
		"""
		DataSource next() method should request live data from market with online datastream
		"""

		return self.__next__()

	def __iter__(self):
		return self

	def __next__(self):
		pass


class PandasDataStream(DataStream):
	"""This class is used to iterate over Yahoo Finance data wrapped in a Pandas Data Frame"""

	def __init__(
		self,
		name: str,
		dataframe: pd.DataFrame,
		offset: int = 0,
		reverse: bool = False,
		date_label: str = "Date",
		window_size: int = 70):

		super(PandasDataStream, self).__init__(name)

		self.dataframe = dataframe
		self.offset = offset
		self.reverse = reverse
		self.time_idx = -self.offset if self.reverse else self.offset
		self.date_label = date_label
		self.window_size = window_size

	def parse_date_column(self):
		def parse_date(date: str):
			try:
				return dt.datetime.strptime(date, "%Y-%m-%d").year
			except ValueError:
				return dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S%z").year
			except Exception as e:
				print(date)
				raise e

		self.dataframe["Year"] = self.dataframe[self.date_label].apply(parse_date)

	def with_daily_returns(self):
		# daily_diff = []
		# for i in range(len(self.dataframe)):
		# 	daily_diff.append(self.get_diff_from_index(self.dataframe.iloc[i].loc["Date"]))
		# self.dataframe["Daily_diff"] = daily_diff
		self.dataframe["Daily_diff"] = self.dataframe["Open"] - self.dataframe["Close"]

	def get_data_by_year(self, y: int):
		return PandasDataStream(
			name=self.name,
			dataframe=self.dataframe.loc[
				self.dataframe["Year"] == y,
			],
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

	def limit_reached(self):
		return (
			(self.reverse and self.time_idx == -len(self.dataframe)-1) or
			(not self.reverse and self.time_idx == len(self.dataframe))
		)

	def get_current_date(self):
		""" Get current Date """
		return self.dataframe.iloc[self.time_idx][self.date_label]

	def get_open(self):
		""" Get current open price """
		return self.dataframe.iloc[self.time_idx]["Open"]

	def get_close(self):
		""" Get current close price """
		return self.dataframe.iloc[self.time_idx]["Close"]

	def get_close_at_index(self, timestamp: str):
		""" Get closing price at specified timestamp """
		x = self.dataframe.loc[self.dataframe[self.date_label] == timestamp, "Close"].to_numpy()
		assert len(x) == 1, "(AssertionError) Timestamp is invalid, date not found or not unique"
		return x[0]

	def get_current_diff(self):
		return self.get_diff_from_index(self.get_current_date())

	def get_diff_from_index(self, timestamp: str):
		""" Computes difference between two successive timestamps """
		x = self.dataframe.index[self.dataframe[self.date_label] == timestamp].to_numpy()
		assert len(x) == 1, "(AssertionError) Timestamp is invalid, date not found or not unique"

		if x == 0:
			return 0
		t1, t2 = self.dataframe.iloc[x-1]["Close"].to_numpy(), self.dataframe.iloc[x]["Close"].to_numpy()
		assert t1.shape == t2.shape and t1.shape == (1,), f"PandasDataStream.get_diff_from_index : {t1} vs {t2}"

		return (t2-t1)[0]

	def get_high(self):
		return self.dataframe.iloc[self.time_idx]["High"]

	def get_low(self):
		return self.dataframe.iloc[self.time_idx]["Low"]

	def get_current_time_index(self):
		return self.time_idx

	def get_window(self):
		if self.reverse and self.time_idx > -len(self.dataframe) + self.window_size:
			return self.dataframe[self.time_idx - self.window_size: self.time_idx]
		elif not self.reverse and self.time_idx < len(self.dataframe) - self.window_size:
			return self.dataframe[self.time_idx: self.time_idx + self.window_size]
		else:
			return None

	def next(self):
		return self.__next__()

	def __iter__(self):
		return self

	def __next__(self):
		self.time_idx += -1 if self.reverse else 1
		if not self.limit_reached():
			return self.dataframe.iloc[self.time_idx]
		else:
			raise StopIteration()
