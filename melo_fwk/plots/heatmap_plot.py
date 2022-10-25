import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

class HeatMapPlotter:

	def __init__(self, df_list: dict):
		self.df_list = df_list

	def save_fig(self, export_folder: str):
		exported_png = []

		for year, df in self.df_list.items():
			filename = f"{export_folder}/HeatMap_{year}.png"
			exported_png.append(filename)

		return exported_png

	@staticmethod
	def save_heatmap_to_png(filename: str, df: pd.DataFrame):
		corr = df.corr()
		fig, ax = plt.subplots(figsize=(15, 10))
		cax = ax.matshow(corr, cmap='RdYlGn')
		for (i, j), z in np.ndenumerate(corr.to_numpy()):
			ax.text(j, i, '{:0.1f}'.format(z), ha='center', va='center')

		plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
		plt.yticks(range(len(corr.columns)), corr.columns)
		fig.colorbar(cax, ticks=[-1, 0, 1], aspect=40, shrink=.8)

		plt.savefig(filename)
		plt.close()

