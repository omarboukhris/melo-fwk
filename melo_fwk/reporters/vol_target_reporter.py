from melo_fwk.config.melo_config import MeloConfig
from melo_fwk.reporters.base_reporter import BaseReporter
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.loggers.global_logger import GlobalLogger

class VolTargetReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		self.logger = GlobalLogger.build_composite_for("VolTargetReporter")
		self.logger.info("Initializing VolTargetReporter")
		super(VolTargetReporter, self).__init__(input_config)

	def header(self):
		self.logger.info("Writing header")
		return self.std_header()

	def process_results(self, query_path: str, export_dir: str, raw_results: dict):
		export_dir = query_path + export_dir
		return ""
