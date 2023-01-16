from typing import Dict

import pandas as pd

from melo_fwk.config import MeloConfig
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.reporters.base_reporter import BaseReporter


class PFAllocationReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		self.logger = GlobalLogger.build_composite_for("PFAllocationReporter")
		self.logger.info("Initializing BacktestReporter")
		super(PFAllocationReporter, self).__init__(input_config)

	def process_results(
		self, query_path: str, export_dir: str,
		raw_results: Dict[str, pd.DataFrame]):
		pass

