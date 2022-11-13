from melo_fwk.config.melo_config import MeloConfig
from melo_fwk.reporters.base_reporter import BaseReporter
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.plots import HeatMapPlotter
from melo_fwk.loggers.global_logger import GlobalLogger

class ClustersReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		self.logger = GlobalLogger.build_composite_for("ClustersReporter")
		self.logger.info("Initializing ClustersReporter")
		super(ClustersReporter, self).__init__(input_config)

	def header(self):
		self.logger.info("Writing header")
		return self.std_header()

	def process_results(self, query_path: str, export_dir: str, raw_results: dict):
		export_dir = query_path + export_dir
		ss = ""
		for year, df in raw_results.items():
			title = f"Correllation Heat Map {year}"
			heatmap_png = f"assets/HeatMap_{year}.png"
			ss += MdFormatter.h2(title)
			ss += MdFormatter.image(title, heatmap_png, f"corr_{year}")

			filename = f"{export_dir}/{heatmap_png}"
			HeatMapPlotter.save_heatmap_to_png(filename, df)

		self.logger.info("Finished Exporting Heat Maps..")
		return ss
