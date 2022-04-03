
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.axes as axes
import matplotlib.dates as mdates


class PricePlotter:
	def __init__(self, dataframe: pd.DataFrame):
		self.df = dataframe

	def plot(self):
		"""make it a scandlestick plot"""
		interval = len(self.df) // 10 if len(self.df) > 10 else 2

		# plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(6))
		plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
		plt.plot(self.df["Date"], self.df[['Open', 'High', 'Low', 'Close']])
		plt.gcf().autofmt_xdate()

	@classmethod
	def save_png(cls, filename: str):
		plt.savefig(filename)
		plt.clf()

	@classmethod
	def show(cls):
		plt.show()


class AccountPlotter:
	def __init__(self, dataframe: pd.DataFrame):
		self.df = dataframe
		self.ylim = None

	def plot(self):
		interval = len(self.df) // 10 if len(self.df) > 10 else 2

		# plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(6))
		self.ylim = self.df[["Balance"]].max(), self.df[["Balance"]].min()
		plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
		plt.plot(self.df["Date"], self.df[['Balance']])
		plt.gcf().autofmt_xdate()
		# plt.show()


	def add_vlines(self, order_book: pd.DataFrame):
		for _, order in order_book.iterrows():
			ymin, ymax = self.ylim
			plt.vlines(order["close_ts"], ymin, ymax, colors="red")

	@classmethod
	def save_png(cls, filename: str):
		plt.savefig(filename)
		plt.clf()

	@classmethod
	def show(cls):
		plt.show()
