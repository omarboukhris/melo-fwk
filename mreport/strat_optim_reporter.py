import os.path
from pathlib import Path

from skopt.plots import plot_objective
import matplotlib.pyplot as plt
import tqdm

from mql.mconfig.melo_config import MeloConfig
from mreport.base_reporter import BaseReporter
from mreport.md_formatter import MdFormatter
from mutils.generic_config_loader import GenericConfigLoader


class StratOptimReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		super(StratOptimReporter, self).__init__(input_config)

	def process_results(self, output_dir: str, export_dir: str, raw_results: dict):
		export_dir = Path(output_dir) / export_dir
		# if not os.path.isdir(output_dir + f"/strat_config_points"):
		# 	os.mkdir(output_dir + f"/strat_config_points")

		self.logger.info("Exporting optimizarion results")
		ss = ""
		for product_name, tsar_dict in tqdm.tqdm(raw_results.items(), leave=False):

			assert isinstance(tsar_dict, dict), \
				f"(BacktestReporter) TSAR result {product_name} is not associated to a dict"

			for strat_name, opt in tsar_dict.items():
				title = strat_name.replace("_", " ")
				opt_result_png = f"assets/{product_name}_{strat_name}.png"
				ss += MdFormatter.h2(title)
				ss += MdFormatter.image(title, opt_result_png, strat_name)

				opt_png = str(export_dir / f"{opt_result_png}")
				_ = plot_objective(opt.optimizer_results_[0], size=4)
				plt.tight_layout()
				plt.savefig(opt_png)
				plt.close()

		self.logger.info("Finished Exporting optimization results..")
		return ss

