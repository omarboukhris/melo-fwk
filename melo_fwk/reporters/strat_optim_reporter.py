import os.path
from dataclasses import asdict
from skopt.plots import plot_objective
import matplotlib.pyplot as plt
import pandas as pd
import tqdm

from melo_fwk.config.melo_config import MeloConfig
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.utils import yaml_io
from melo_fwk.utils.quantflow_factory import QuantFlowFactory


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
		self.strat_list = [str(list(x)[0]) for x in input_config.strategies_config[0]]
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

	def process_results(self, query_path: str, export_dir: str, raw_results: dict):
		export_dir = query_path + export_dir
		if not os.path.isdir(query_path + f"/strat_config_points"):
			os.mkdir(query_path + f"/strat_config_points")

		self.logger.info("Exporting optimizarion results")
		ss = ""
		for product_name, tsar_dict in tqdm.tqdm(raw_results.items(), leave=False):

			assert isinstance(tsar_dict, dict), \
				f"(BacktestReporter) TSAR result {product_name} is not associated to a dict"


			for strat_name, opt in tsar_dict.items():
				self._export_config_points(opt, query_path, strat_name)

				title = strat_name.replace("_", " ")
				opt_result_png = f"assets/{product_name}_{strat_name}.png"
				ss += MdFormatter.h2(title)
				ss += MdFormatter.image(title, opt_result_png, strat_name)

				opt_png = f"{export_dir}/{opt_result_png}"
				plt.figure(figsize=(10, 10))
				_ = plot_objective(opt.optimizer_results_[0])
				plt.savefig(opt_png)
				plt.close()

		self.logger.info("Finished Exporting optimization results..")
		return ss

	@staticmethod
	def _export_config_points(opt, query_path, strat_name):
		strat_config_df = pd.DataFrame({
			"score_vals": -opt.optimizer_results_[0].func_vals,
			"x_iters": opt.optimizer_results_[0].x_iters
		}).sort_values(by=["score_vals"], ascending=False).drop_duplicates(subset=["score_vals"])
		# might eliminate different candidates with exact same score (low probability but exists)

		config_list = {}
		strat_class_ = QuantFlowFactory.get_strategy(strat_name)
		for i, (_, config_pt) in enumerate(strat_config_df.iterrows()):
			params = config_pt["x_iters"]
			strat = asdict(strat_class_(*params).estimate_forecast_scale())
			strat.pop("search_space", None)
			config_list[f"{strat_name}_{i}"] = strat

		yaml_io.write_strat_config_point(config_list, query_path + f"/strat_config_points/{strat_name}.yml")
