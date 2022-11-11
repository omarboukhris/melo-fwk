import tqdm

from melo_fwk.config.melo_config import MeloConfig
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.loggers.global_logger import GlobalLogger

class ForecastWeightsReporter:

	def __init__(self, input_config: MeloConfig):
		"""
		Displays input parameter responsible for the generated results
		Could be report header

		:param input_config:
		:return:
		"""
		self.logger = GlobalLogger.build_composite_for("ForecastWeightsReporter")
		self.logger.info("Initializing Reporter")
		# name:
		self.name = input_config.name

		# products:
		self.products_name_list = list(input_config.products_config[0].keys())
		self.begin, self.end = input_config.products_config[1]

		# size policy:
		self.size_policy = input_config.size_policy

		# strategies:
		self.strat_list = [str(x) for x in input_config.strategies_config[0]]
		self.fw = input_config.strategies_config[1]

	def header(self):
		self.logger.info("Writing header")

		ss = MdFormatter.h1(f"Backtest - {self.name} from {self.begin} to {self.end}")
		ss += MdFormatter.h2("Products:")
		ss += MdFormatter.item_list(self.products_name_list)

		ss += MdFormatter.h2("VolTarget - Position Size:")
		ss += "Using " + MdFormatter.italic(type(self.size_policy).__name__) + " for Position Sizing\n"

		ss += MdFormatter.h2("Strategies:")
		ss += MdFormatter.item_list([f"{w} x {strat}" for w, strat in zip(self.fw, self.strat_list)])

		return ss

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
