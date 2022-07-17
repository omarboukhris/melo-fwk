
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
	def __init__(self, dataframe: pd.DataFrame, twinx_dataframe: pd.DataFrame = None):
		self.df = dataframe
		self.twin_df = twinx_dataframe
		self.ylim = None

	@staticmethod
	def align_yaxis(ax1, v1, ax2, v2):
		"""adjust ax2 ylimit so that v2 in ax2 is aligned to v1 in ax1"""
		_, y1 = ax1.transData.transform((0, v1))
		_, y2 = ax2.transData.transform((0, v2))
		inv = ax2.transData.inverted()
		_, dy = inv.transform((0, 0)) - inv.transform((0, y1 - y2))
		miny, maxy = ax2.get_ylim()
		ax2.set_ylim(miny + dy, maxy + dy)

	@staticmethod
	def plot_df(df: pd.DataFrame, x_label: str, y_label: str, ax, color: str = "blue"):
		interval = len(df) // 10 if len(df) > 10 else 2
		plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
		ax.plot(df[x_label], df[[y_label]], color=color)
		plt.gcf().autofmt_xdate()

		return ax

	def plot(self):
		_, ax = plt.subplots()
		self.ylim = self.df[["Balance"]].max(), self.df[["Balance"]].min()
		AccountPlotter.plot_df(self.df, x_label="Date", y_label="Balance", ax=ax)

	def plot_twinx(self):
		_, ax1 = plt.subplots()
		AccountPlotter.plot_df(self.df, x_label="Date", y_label="Balance", ax=ax1, color="blue")
		ax2 = ax1.twinx()
		AccountPlotter.plot_df(self.twin_df, x_label="Date", y_label="Close", ax=ax2, color="green")
		# AccountPlotter.align_yaxis(ax1, 0, ax2, 0)

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
