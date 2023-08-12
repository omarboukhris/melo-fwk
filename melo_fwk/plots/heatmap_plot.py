from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from mutils.generic_config_loader import GenericConfigLoader


class HeatMapPlotter:

	def __init__(self, df_list: dict):
		self.df_list = df_list
		self.working_dir = Path(GenericConfigLoader.get_node("working_dir", "."))

	def save_fig(self, export_folder: str):
		exported_png = []

		for year, df in self.df_list.items():
			filename = f"{export_folder}/HeatMap_{year}.png"
			exported_png.append(str(self.working_dir / filename))

		return exported_png

	@staticmethod
	def save_heatmap_to_png(filename: str, corr: pd.DataFrame):
		working_dir = Path(GenericConfigLoader.get_node("working_dir", "."))
		fig, ax = plt.subplots(figsize=(15, 10))
		cax = ax.matshow(corr, cmap='RdYlGn')  # or jet
		for (i, j), z in np.ndenumerate(corr.to_numpy()):
			ax.text(j, i, '{:0.3f}'.format(z), ha='center', va='center')

		plt.xticks(range(len(corr.columns)), corr.columns, rotation=90)
		plt.yticks(range(len(corr.columns)), corr.columns)
		fig.colorbar(cax, ticks=[-1, 0, 1], aspect=40, shrink=.8)

		plt.tight_layout()
		plt.savefig(str(working_dir / filename))
		plt.close()

