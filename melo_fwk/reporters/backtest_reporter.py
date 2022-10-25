import tqdm

from melo_fwk.config.melo_config import MeloConfig
from melo_fwk.reporters.utils.md_formatter import MdFormatter
from melo_fwk.plots import TsarPlotter
from melo_fwk.loggers.global_logger import GlobalLogger

class BacktestReporter:

	def __init__(self, input_config: MeloConfig):
		"""
		Displays input parameter responsible for the generated results
		Could be report header

		:param input_config:
		:return:
		"""
		self.logger = GlobalLogger.build_composite_for("BacktestReporter")
		self.logger.info("Initializing BacktestReporter")
		# name:
		self.name = input_config.name

		# products:
		self.products_name_list = list(input_config.products_config[0].keys())
		self.begin, self.end = input_config.products_config[1]

		# size policy:
		self.vol_target = input_config.vol_target
		self.size_policy_class_ = input_config.size_policy_class_

		# strategies:
		self.strat_list = [str(x) for x in input_config.strategies_config[0]]
		self.fw = input_config.strategies_config[1]

	def header(self):
		self.logger.info("Writing header")

		ss = MdFormatter.h1(f"Backtest - {self.name} from {self.begin} to {self.end}")
		ss += MdFormatter.h2("Products:")
		ss += MdFormatter.item_list(self.products_name_list)

		ss += MdFormatter.h2("VolTarget:")
		ss += MdFormatter.italic(str(self.size_policy_class_)) + "\n"
		ss += MdFormatter.item_list(str(self.vol_target).split("\n")[:-1])

		ss += MdFormatter.h2("Strategies:")
		ss += MdFormatter.item_list([f"{w} x {strat}" for w, strat in zip(self.fw, self.strat_list)])

		return ss

	def process_results(self, export_dir: str, raw_results: dict):
		"""
		raw_results dict :
			key = product name
			Value = dict :
				key = product_filepath + year
				value = TSAR
		"""
		self.logger.info("Exporting Tsar data")
		ss = ""
		for product_name, tsar_dict in tqdm.tqdm(raw_results.items(), leave=False):

			assert isinstance(tsar_dict, dict), \
				f"(BacktestReporter) TSAR result {product_name} is not associated to a dict"

			for prod_fn_y, tsar in tsar_dict.items():
				tsar_png = f"{export_dir}/assets/{prod_fn_y}.png"
				TsarPlotter.save_tsar_as_png(tsar_png, tsar)

				title = prod_fn_y.replace("_", " ")
				tsar_png = f"assets/{prod_fn_y}.png"
				ss += MdFormatter.h2(title)
				ss += MdFormatter.image(title, tsar_png, prod_fn_y)

		self.logger.info("Finished Exporting Tsar Data..")
		return ss
