import matplotlib.pyplot as plt

from mql.mconfig.melo_config import MeloConfig
from mreport.base_reporter import BaseReporter
from mreport.md_formatter import MdFormatter
from melo_fwk.plots import HeatMapPlotter


class ClustersReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		super(ClustersReporter, self).__init__(input_config)

	def process_results(self, query_path: str, export_dir: str, raw_results: tuple):
		export_dir = query_path + export_dir
		avg_corr, corr_hist = raw_results

		title = f"Average Correllation Heat Map"
		heatmap_png = f"assets/avg_HeatMap.png"
		ss = MdFormatter.h2(title)
		ss += MdFormatter.image(title, heatmap_png, f"avg_corr")

		filename = f"{export_dir}/{heatmap_png}"
		HeatMapPlotter.save_heatmap_to_png(filename, avg_corr)

		for k, population in corr_hist.items():
			title = f"{k.split(':')} Correllation Histogram"
			image_name = k.replace(":", "_").replace(".", "_")
			heatmap_png = f"assets/{image_name}_corr.png"
			ss += MdFormatter.h2(title)
			ss += MdFormatter.image(title, heatmap_png, f"{image_name}_corr")

			filename = f"{export_dir}/{heatmap_png}"
			plt.hist(population, bins=len(population)//2)
			plt.title(title)
			plt.savefig(filename)
			plt.close()

		self.logger.info("Finished Exporting Heat Maps..")
		return ss
