from typing import Dict, Tuple

import pandas as pd

from melo_fwk.config import MeloConfig
from melo_fwk.config.melo_clusters_config import MeloClustersConfig
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.reporters.base_reporter import GenericReporter


class PFAllocationReporter(GenericReporter):

	def __init__(self, input_config: MeloClustersConfig):
		self.logger = GlobalLogger.build_composite_for("PFAllocationReporter")
		self.logger.info("Initializing BacktestReporter")
		super(PFAllocationReporter, self).__init__(input_config)

	def header(self):
		pass

	def process_results(
		self, query_path: str, export_dir: str,
		raw_results: Tuple[Dict[str, pd.DataFrame], pd.DataFrame]):

		clusters_optim_map, portfolio_optim_df = raw_results
		for ckey, optim_result_df in clusters_optim_map.items():
			# superimpose hist for weights
			# hist "fun" -> score
			# hist div_mult
			pass


		pass

