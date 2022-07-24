
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


class AbstractPlotter:
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

	def add_vlines(self, order_book: pd.DataFrame):
		for _, order in order_book.iterrows():
			ymin, ymax = self.ylim
			plt.vlines(order["close_ts"], ymin, ymax, colors="red")

	@staticmethod
	def plot_df(df: pd.DataFrame, x_label: str, y_label, ax, color: str = "blue"):
		interval = len(df) // 10 if len(df) > 10 else 2
		plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=interval))
		ax.plot(df[x_label], df[y_label], color=color)
		plt.gcf().autofmt_xdate()

		return ax

	def _render(self, render_plot: callable):
		if self.twin_df is None:
			_ = self.plot()
			render_plot()
		else:
			_, _ = self.plot_twinx()
			render_plot()

	def save_png(self, filename: str):
		def save_fig():
			plt.savefig(filename)
			plt.close()
		self._render(save_fig)

	def plot(self):
		_, ax = plt.subplots()
		return ax

	def plot_twinx(self):
		_, ax1 = plt.subplots()
		ax2 = ax1.twinx()
		return ax1, ax2

	def show(self):
		def show_plot():
			plt.show()
			plt.close()
		self._render(show_plot)

class AccountPlotter(AbstractPlotter):
	def __init__(self, dataframe: pd.DataFrame, twinx_dataframe: pd.DataFrame = None):
		super(AccountPlotter, self).__init__(dataframe, twinx_dataframe)

	def plot(self):
		_, ax = plt.subplots()
		self.ylim = self.df[["Balance"]].max(), self.df[["Balance"]].min()
		AbstractPlotter.plot_df(self.df, x_label="Date", y_label=["Balance"], ax=ax)
		return ax

	def plot_twinx(self):
		_, ax1 = plt.subplots()
		AbstractPlotter.plot_df(self.df, x_label="Date", y_label=["Balance"], ax=ax1, color="blue")
		ax2 = ax1.twinx()
		AbstractPlotter.plot_df(self.twin_df, x_label="Date", y_label=["Close"], ax=ax2, color="green")
		return ax1, ax2

class PricePlotter(AbstractPlotter):
	def __init__(self, dataframe: pd.DataFrame):
		super(PricePlotter, self).__init__(dataframe)

	def plot(self):
		_, ax = plt.subplots()
		self.ylim = self.df[["Close"]].max(), self.df[["Close"]].min()
		AbstractPlotter.plot_df(self.df, x_label="Date", y_label=['Open', 'High', 'Low', 'Close'], ax=ax)
		return ax

class ForecastPlotter(AbstractPlotter):
	def __init__(self, dataframe: pd.DataFrame, twinx_dataframe: pd.DataFrame = None):
		super(ForecastPlotter, self).__init__(dataframe, twinx_dataframe)

	def plot(self):
		_, ax = plt.subplots()
		self.ylim = self.df[["Forecast"]].max(), self.df[["Forecast"]].min()
		AbstractPlotter.plot_df(self.df, x_label="Date", y_label=["Forecast"], ax=ax)
		return ax

	def plot_twinx(self):
		_, ax1 = plt.subplots()
		AbstractPlotter.plot_df(self.df, x_label="Date", y_label=["Forecast"], ax=ax1, color="blue")
		ax2 = ax1.twinx()
		AbstractPlotter.plot_df(self.twin_df, x_label="Date", y_label=["Close"], ax=ax2, color="green")
		return ax1, ax2

	def add_vlines(self, order_book: pd.DataFrame):
		for _, order in order_book.iterrows():
			ymin, ymax = self.ylim
			plt.vlines(order["close_ts"], ymin, ymax, colors="red")
