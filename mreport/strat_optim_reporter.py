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

	def process_results(self, query_path: str, export_dir: str, raw_results: dict):
		strat_optim_report_config_node = GenericConfigLoader.get_node(StratOptimReporter.__name__, {})
		strat_config_points_path = strat_optim_report_config_node.get(
			"strat_config_points", str(Path(query_path) / "strat_config_points"))
		export_dir = query_path + export_dir
		if not os.path.isdir(query_path + f"/strat_config_points"):
			os.mkdir(query_path + f"/strat_config_points")

		self.logger.info("Exporting optimizarion results")
		ss = ""
		for product_name, tsar_dict in tqdm.tqdm(raw_results.items(), leave=False):

			assert isinstance(tsar_dict, dict), \
				f"(BacktestReporter) TSAR result {product_name} is not associated to a dict"

			for strat_name, opt in tsar_dict.items():
				StratConfigRegistry.export_strat_config_node(opt, strat_config_points_path, strat_name)

				title = strat_name.replace("_", " ")
				opt_result_png = f"assets/{product_name}_{strat_name}.png"
				ss += MdFormatter.h2(title)
				ss += MdFormatter.image(title, opt_result_png, strat_name)

				opt_png = f"{export_dir}/{opt_result_png}"
				_ = plot_objective(opt.optimizer_results_[0], size=4)
				plt.tight_layout()
				plt.savefig(opt_png)
				plt.close()

		self.logger.info("Finished Exporting optimization results..")
		return ss

