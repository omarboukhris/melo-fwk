
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class GenericPlotter:
	def __init__(self, dataframe: pd.DataFrame, twinx_dataframe: pd.DataFrame = None):
		self.df = dataframe
		self.twin_df = twinx_dataframe

	def save_png(self, filename: str, df_ylabel, twindf_ylabel, yscale: str = "linear"):
		fig, ax1 = plt.subplots()
		interval = len(self.df) // 10 if len(self.df) > 10 else 2
		plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
		self.df.plot(x="Date", y=df_ylabel, ax=ax1, color="blue")
		plt.gcf().autofmt_xdate()

		if self.twin_df is not None and twindf_ylabel is not None:
			ax2 = ax1.twinx()
			interval = len(self.df) // 10 if len(self.df) > 10 else 2
			plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
			self.twin_df.plot(x="Date", y=twindf_ylabel, ax=ax2, color="green")
			plt.gcf().autofmt_xdate()

		plt.grid()
		plt.yscale(yscale)
		plt.savefig(filename)
		plt.close(fig)

class AccountPlotter:
	def __init__(self, dataframe: pd.DataFrame, twinx_dataframe: pd.DataFrame = None):
		self.generic_plotter = GenericPlotter(dataframe, twinx_dataframe)

	def save_png(self, filename: str):
		self.generic_plotter.save_png(filename, "Balance", "Close", "log")

class HLOCPricePlotter:
	def __init__(self, dataframe: pd.DataFrame):
		self.generic_plotter = GenericPlotter(dataframe, None)

	def save_png(self, filename: str):
		self.generic_plotter.save_png(filename, ['Open', 'High', 'Low', 'Close'], None)

class ForecastPlotter:
	def __init__(self, dataframe: pd.DataFrame, twinx_dataframe: pd.DataFrame = None):
		self.generic_plotter = GenericPlotter(dataframe, twinx_dataframe)

	def save_png(self, filename: str):
		self.generic_plotter.save_png(filename, "Forecast", "Close")
