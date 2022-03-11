
import pandas as pd
import numpy as np

class DataStream:
	def __init__(self):
		pass

	def get_data(self):
		pass

	def get_current_date(self):
		pass

	def get_open(self):
		pass

	def get_close(self):
		pass

	def get_close_at_index(self, timestamp: str):
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
		return self.__next__()

	def __iter__(self):
		return self

	def __next__(self):
		pass


class PandasDataStream(DataStream):
	"""This class is used to iterate over Yahoo Finance data wrapped in a Pandas Data Frame"""

	def __init__(
		self,
		dataframe: pd.DataFrame,
		reverse: bool = False,
		date_label: str = "Date",
		window_size: int = 200):

		super(PandasDataStream, self).__init__()

		self.dataframe = dataframe
		self.time_idx = 0
		self.reverse = reverse
		self.date_label = date_label
		self.window_size = window_size

	def reset(self):
		self.time_idx = 0

	def get_data(self):
		return self.dataframe

	def limit_reached(self):
		return (
			(self.reverse and self.time_idx == -len(self.dataframe)-1) or
			(not self.reverse and self.time_idx == len(self.dataframe))
		)

	def get_current_date(self):
		return self.dataframe.iloc[self.time_idx][self.date_label]

	def get_open(self):
		return self.dataframe.iloc[self.time_idx]["Open"]

	def get_close(self):
		return self.dataframe.iloc[self.time_idx]["Close"]

	def get_close_at_index(self, timestamp: str):
		x = self.dataframe.loc[self.dataframe[self.date_label] == timestamp, "Close"].to_numpy()
		assert len(x) == 1, "(AssertionError) Timestamp is invalid, date not found or not unique"
		return x[0]

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


class PandasDataStreamHourly(PandasDataStream):
	def __init__(self, dataframe: pd.DataFrame, reverse: bool = True):
		super(PandasDataStreamHourly, self).__init__(dataframe, reverse, "Datetime")


if __name__ == "__main__":

	pdstream = PandasDataStream(pd.read_csv("../data/FB_1d_10y.csv"))

	for tick in pdstream:
		assert pdstream.get_current_date() == tick["Date"], "dates are different"
		assert pdstream.get_open() == tick["Open"], "open prices are different"
		print(tick["Date"], "//", tick["Open"])

