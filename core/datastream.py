
import pandas as pd

class DataStream:
	def __init__(self):
		pass

	def get_current_date(self):
		pass

	def get_open(self):
		pass

	def get_close(self):
		pass

	def get_high(self):
		pass

	def get_low(self):
		pass

	def get_current_time_index(self):
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

	def __init__(self, dataframe: pd.DataFrame, reverse: bool = True, date_label: str = "Date"):
		
		super(PandasDataStream, self).__init__()

		self.dataframe = dataframe
		self.time_idx = 0
		self.reverse = reverse
		self.date_label = date_label

	def reset(self):
		self.time_idx = 0

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

	def get_high(self):
		return self.dataframe.iloc[self.time_idx]["High"]

	def get_low(self):
		return self.dataframe.iloc[self.time_idx]["Low"]

	def get_current_time_index(self):
		return self.time_idx

	def next(self):
		return self.__next__()

	def __iter__(self):
		return self

	def __next__(self):
		try:
			self.time_idx += -1 if self.reverse else 1
			return self.dataframe.iloc[self.time_idx]

		except IndexError:
			self.reset()
			raise StopIteration()


if __name__ == "__main__":
	pdstream = PandasDataStream(pd.read_csv("data/FB_1d_10y.csv"))

	for tick in pdstream:
		assert pdstream.get_current_date() == tick["Date"], "dates are different"
		assert pdstream.get_open() == tick["Open"], "open prices are different"
		print(tick["Date"], "//", tick["Open"])
