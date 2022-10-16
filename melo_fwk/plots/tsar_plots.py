
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

import tqdm

class TsarPlotter:
	def __init__(self, tsar_list: dict):
		self.tsar_list = tsar_list

	def save_fig(self):

		for product_name, tsar_entry in tqdm.tqdm(self.tsar_list.items()):
			for filename, tsar in tsar_entry.items():

				fig = plt.figure(figsize=(30, 20))
				gs = GridSpec(nrows=5, ncols=2)
				ax0 = fig.add_subplot(gs[0, :])
				ax1 = fig.add_subplot(gs[1, :])
				ax2 = fig.add_subplot(gs[2, :])
				ax3 = fig.add_subplot(gs[3, :])
				ax4 = fig.add_subplot(gs[4, :])

				plt.subplots_adjust(hspace=.0)

				tsar.price_series.plot(y="Price", ax=ax0, color="green")
				tsar.account_series.plot(y="Account", ax=ax1, color="red")
				tsar.daily_pnl_series.plot(y="Daily_PnL", ax=ax2, color="black")
				tsar.forecast_series.plot(y="Forecast", ax=ax3, color="blue")
				tsar.size_series.plot(y="Size", ax=ax4, color="cyan")

				ax0.grid()
				ax1.grid()
				ax2.grid()
				ax3.grid()
				ax4.grid()

				plt.savefig(f"{filename}.png")
				plt.close()
