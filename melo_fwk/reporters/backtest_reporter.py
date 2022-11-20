import tqdm

from melo_fwk.config.melo_config import MeloConfig
from melo_fwk.reporters.base_reporter import BaseReporter
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.plots import TsarPlotter
from melo_fwk.loggers.global_logger import GlobalLogger

class BacktestReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		self.logger = GlobalLogger.build_composite_for("BacktestReporter")
		self.logger.info("Initializing BacktestReporter")
		super(BacktestReporter, self).__init__(input_config)

	def process_results(self, query_path: str, export_dir: str, raw_results: dict):
		"""
		raw_results dict :
			key = product name
			Value = dict :
				key = product_filepath + year
				value = TSAR
		"""
		export_dir = query_path + export_dir
		self.logger.info("Exporting Tsar data")
		ss = ""
		for product_name, tsar_dict in tqdm.tqdm(raw_results.items(), leave=False):

			assert isinstance(tsar_dict, dict), \
				f"(BacktestReporter) TSAR result {product_name} is not associated to a dict"

			for prod_fn_y, tsar in tsar_dict.items():
				title = prod_fn_y.replace("_", " ")
				tsar_png = f"assets/{prod_fn_y}.png"
				ss += MdFormatter.h2(title)
				metrics = [
					f"Sharpe ratio  : {tsar.sharpe_ratio()}",
					f"Sortino ratio : {tsar.sortino_ratio()}",
					f"Max Drawdown  : {tsar.max_drawdown()}",
					f"Calmar ration : {tsar.calmar_ratio()}",
				]
				ss += MdFormatter.item_list(metrics)
				ss += MdFormatter.image(title, tsar_png, prod_fn_y)

				tsar_png = f"{export_dir}/{tsar_png}"
				TsarPlotter.save_tsar_as_png(tsar_png, tsar)

		self.logger.info("Finished Exporting Tsar data..")
		return ss
