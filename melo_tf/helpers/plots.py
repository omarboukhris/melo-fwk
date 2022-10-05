
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class AccountPlotter:
	def __init__(self, dataframe: pd.DataFrame, twinx_dataframe: pd.DataFrame = None):
		self.df = dataframe
		self.twin_df = twinx_dataframe

	def save_png(self, filename: str):
		fig, ax1 = plt.subplots()
		interval = len(self.df) // 10 if len(self.df) > 10 else 2
		plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
		self.df.plot(x="Date", y="Balance", ax=ax1, color="blue")
		plt.gcf().autofmt_xdate()

		if self.twin_df is not None:
			ax2 = ax1.twinx()
			interval = len(self.df) // 10 if len(self.df) > 10 else 2
			plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
			self.twin_df.plot(x="Date", y="Close", ax=ax2, color="green")
			plt.gcf().autofmt_xdate()

		plt.savefig(filename)
		plt.grid()
		plt.close(fig)
		plt.close()

class HLOCPricePlotter:
	def __init__(self, dataframe: pd.DataFrame):
		self.df = dataframe

	def save_png(self, filename: str):
		fig, ax1 = plt.subplots()
		interval = len(self.df) // 10 if len(self.df) > 10 else 2
		plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
		self.df.plot(x="Date", y=['Open', 'High', 'Low', 'Close'], ax=ax1, color="blue")
		plt.gcf().autofmt_xdate()
		plt.grid()
		plt.savefig(filename)
		plt.close(fig)
		plt.close()


class ForecastPlotter:
	def __init__(self, dataframe: pd.DataFrame, twinx_dataframe: pd.DataFrame = None):
		self.df = dataframe
		self.twin_df = twinx_dataframe

	def save_png(self, filename: str):
		fig, ax1 = plt.subplots()
		interval = len(self.df) // 10 if len(self.df) > 10 else 2
		plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
		self.df.plot(x="Date", y="Forecast", ax=ax1, color="blue")
		plt.grid()
		plt.gcf().autofmt_xdate()

		if self.twin_df is not None:
			ax2 = ax1.twinx()
			interval = len(self.df) // 10 if len(self.df) > 10 else 2
			plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
			self.twin_df.plot(x="Date", y="Close", ax=ax2, color="green")
			plt.gcf().autofmt_xdate()

		plt.savefig(filename)
		plt.close(fig)
		plt.close()
