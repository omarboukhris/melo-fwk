import tqdm

from melo_fwk.config.melo_config import MeloConfig
from melo_fwk.reporters.base_reporter import BaseReporter
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.loggers.global_logger import GlobalLogger

class ForecastWeightsReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		self.logger = GlobalLogger.build_composite_for("ForecastWeightsReporter")
		self.logger.info("Initializing ForecastWeightsReporter")
		super(ForecastWeightsReporter, self).__init__(input_config)

	def header(self):
		self.logger.info("Writing header")
		return self.std_header()

	def process_results(self, query_path: str, export_dir: str, raw_results: dict):
		export_dir = query_path + export_dir
		self.logger.info("Exporting optimizarion results")
		ss = MdFormatter.h2("Optimization Results")
		for product_name, opt_dict in tqdm.tqdm(raw_results.items(), leave=False):

			assert isinstance(opt_dict, dict), \
				f"(ForecastWeightsReporter) TSAR result {product_name} is not associated to a list"

			ss += MdFormatter.bold(f"For product {MdFormatter.italic(product_name)}") + "\n"
			opt_items = []
			for year, opt in opt_dict.items():
				sr = -opt["OptimResult"].fun
				fw = opt["OptimResult"].x
				div_mult = opt["DivMult"]

				opt_items.append(f"Year {year}: forecast weight are {fw} with multiplier {div_mult} producing SR of {sr}")

			ss += MdFormatter.item_list(opt_items) + "\n"

		return ss
