
import pandas as pd
import matplotlib.pyplot as plt
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
		plt.show()

class AccountPlotter:
	def __init__(self, dataframe: pd.DataFrame):
		self.df = dataframe

	def plot(self):
		interval = len(self.df) // 10 if len(self.df) > 10 else 2

		# plt.gca().xaxis.set_major_locator(ticker.MaxNLocator(6))
		plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
		plt.plot(self.df["Date"], self.df[['Balance']])
		plt.gcf().autofmt_xdate()
		plt.show()

