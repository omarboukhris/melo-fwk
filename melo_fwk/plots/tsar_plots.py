
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.gridspec import GridSpec

import tqdm

class TsarPlotter:
	def __init__(self, tsar_list: dict):
		self.tsar_list = tsar_list

	def save_fig(self):

		for product_name, tsar_entry in tqdm.tqdm(self.tsar_list.items()):
			for filename, tsar in tqdm.tqdm(tsar_entry.items()):
				series_list = [
					tsar.price_series,
					tsar.account_series,
					tsar.daily_pnl_series,
					tsar.forecast_series,
					tsar.size_series.set_axis(tsar.dates),
				]
				column_list = ["Price", "Account", "Daily_PnL", "Forecast", "Size"]
				label_list = ["Price", "Account", "Daily PnL", "Forecast", "Size"]
				colors_list = ["green", "red", "black", "blue", "cyan"]

				fig = plt.figure(figsize=(21, 14))
				gs = GridSpec(nrows=5, ncols=2)

				for i, series, column, label, colors in zip(range(len(column_list)), series_list, column_list, label_list, colors_list):

					ax = fig.add_subplot(gs[i, :])
					series.fillna(0).plot(y=column, ax=ax, color=colors)
					ax.set_ylabel(label)
					ax.grid()

				plt.subplots_adjust(hspace=.0)
				plt.xlabel("Time")
				plt.savefig(f"{filename}.png")
				plt.close()
