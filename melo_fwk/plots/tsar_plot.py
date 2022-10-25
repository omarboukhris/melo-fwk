
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.gridspec import GridSpec

import tqdm

from melo_fwk.datastreams import TsarDataStream


class TsarPlotter:
	column_list = ["Price", "Account", "Daily_PnL", "Forecast", "Size"]
	label_list = ["Price", "Account", "Daily PnL", "Forecast", "Size"]
	colors_list = ["green", "red", "black", "blue", "cyan"]

	def __init__(self, tsar_list: dict):
		self.tsar_list = tsar_list

	def save_fig(self, export_folder: str):

		exported_png = []
		for product_name, tsar_entry in tqdm.tqdm(self.tsar_list.items(), leave=False):
			for filename, tsar in tqdm.tqdm(tsar_entry.items()):
				png_export_file = f"{export_folder}/{filename}.png"
				self.save_tsar_as_png(png_export_file, tsar)
				exported_png.append(png_export_file)

		return exported_png

	@staticmethod
	def save_tsar_as_png(filename: str, tsar: TsarDataStream):
		series_list = [
			tsar.price_series,
			tsar.account_series,
			tsar.daily_pnl_series,
			tsar.forecast_series,
			tsar.size_series.set_axis(tsar.dates),
		]
		fig = plt.figure(figsize=(21, 14))
		gs = GridSpec(nrows=5, ncols=2)
		for i, series, column, label, colors in zip(range(len(TsarPlotter.column_list)), series_list,
													TsarPlotter.column_list, TsarPlotter.label_list,
													TsarPlotter.colors_list):
			ax = fig.add_subplot(gs[i, :])
			series.fillna(0).plot(y=column, ax=ax, color=colors)
			ax.set_ylabel(label)
			ax.grid()
		plt.subplots_adjust(hspace=.0)
		plt.xlabel("Time")
		plt.savefig(filename)
		plt.close()
