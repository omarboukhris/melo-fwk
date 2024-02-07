from typing import Dict, Tuple, List

import pandas as pd

from mql.mconfig.melo_books_config import MeloBooksConfig
from mutils.loggers.global_logger import GlobalLogger
from mreport.base_reporter import GenericReporter


class PFAllocationReporter(GenericReporter):

	def __init__(self, input_config: MeloBooksConfig):
		self.logger = GlobalLogger.build_composite_for("PFAllocationReporter")
		self.logger.info("Initializing BacktestReporter")
		super(PFAllocationReporter, self).__init__(input_config)

	def header(self):
		ss = ""
		return ss

	def process_results(
		self, query_path: str, export_dir: str,
		raw_results: Tuple[Dict[str, pd.DataFrame], pd.DataFrame, List, List]):

		ss = ""

		clusters_optim_map, portfolio_optim_df, var_profiles, weights = raw_results
		for ckey, optim_result_df in clusters_optim_map.items():
			# superimpose hist for weights
			# hist "fun" -> score
			# hist div_mult
			pass



		return ss

