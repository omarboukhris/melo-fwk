from typing import Tuple

import tqdm

from melo_fwk.basket.var_basket import VaRBasket
from melo_fwk.config.melo_config import MeloConfig
from melo_fwk.reporters.base_reporter import BaseReporter
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.plots.var_plot import VarPlotter
from melo_fwk.loggers.global_logger import GlobalLogger

class VaRReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		self.logger = GlobalLogger.build_composite_for("BacktestReporter")
		self.logger.info("Initializing BacktestReporter")
		super(VaRReporter, self).__init__(input_config)

	def process_results(
		self, query_path: str, export_dir: str,
		raw_results: Tuple[dict, VaRBasket]):
		"""
		raw_results dict :
			key = product name
			Value = dict :
				key = product_filepath + year
				value = TSAR
		"""
		out_dict, var_basket = raw_results
		export_dir = query_path + export_dir
		self.logger.info("Exporting VaR Results")
		ss = ""

		# VarPlotter.plot_prices(basket.simulate_hist(n_days, r_spl))
		# VarPlotter.plot_prices(basket.simulate_price(n_days, n_sim))
		# VarPlotter.plot_price_paths(basket.simulate_price_paths(n_days, n_sim), basket.tails)
		# VarPlotter.plot_price_paths(basket.simulate_hist_paths(n_days, r_spl), basket.tails)

		return ss
