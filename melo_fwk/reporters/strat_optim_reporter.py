import matplotlib.pyplot as plt
import tqdm
from skopt.plots import plot_objective

from melo_fwk.config.melo_config import MeloConfig
from melo_fwk.reporters.utils.md_formatter import MdFormatter
from melo_fwk.plots import TsarPlotter
from melo_fwk.loggers.global_logger import GlobalLogger

class StratOptimReporter:

	def __init__(self, input_config: MeloConfig):
		"""
		Displays input parameter responsible for the generated results
		Could be report header

		:param input_config:
		:return:
		"""
		self.logger = GlobalLogger.build_composite_for("StratOptimReporter")
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

		ss += MdFormatter.h2("VolTarget:")
		ss += "Using " + MdFormatter.italic(type(self.size_policy).__name__) + " for Position Sizing\n"

		ss += MdFormatter.h2("Strategies:")
		ss += MdFormatter.item_list([f"{w} x {strat}" for w, strat in zip(self.fw, self.strat_list)])

		return ss

	def process_results(self, export_dir: str, raw_results: dict):
		# ax = plot_objective(opt.optimizer_results_[0])
		# plt.show()
		self.logger.info("Exporting optimizarion results")
		ss = ""
		for product_name, tsar_dict in tqdm.tqdm(raw_results.items(), leave=False):

			assert isinstance(tsar_dict, dict), \
				f"(BacktestReporter) TSAR result {product_name} is not associated to a dict"

			for prod_fn_y, opt in tsar_dict.items():
				title = prod_fn_y.replace("_", " ")
				opt_result_png = f"assets/{prod_fn_y}.png"
				ss += MdFormatter.h2(title)
				ss += MdFormatter.image(title, opt_result_png, prod_fn_y)

				opt_png = f"{export_dir}/{opt_result_png}"
				plt.figure(figsize=(10, 10))
				_ = plot_objective(opt.optimizer_results_[0])
				plt.savefig(opt_png)
				plt.close()

		self.logger.info("Finished Exporting optimization results..")
		return ss
