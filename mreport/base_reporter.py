from mql.mconfig import MeloConfig
from mql.mconfig.common_melo_config import CommonMeloConfig
from mutils.loggers.global_logger import GlobalLogger
from mreport.md_formatter import MdFormatter


class GenericReporter:
	def __init__(self, input_config: CommonMeloConfig):
		self.name = input_config.name
		self.reporter_class = str(input_config.reporter_class_)

class BaseReporter(GenericReporter):
	def __init__(self, input_config: MeloConfig):
		"""
		Displays input parameter responsible for the generated results
		Could be report header

		:param input_config:
		:return:
		"""
		super().__init__(input_config)
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)

		# name:
		self.name = input_config.name

		# products:
		self.products_name_list = list(input_config.products_config[0].keys())
		self.begin, self.end = input_config.products_config[1]

		# size policy:
		self.size_policy = input_config.size_policy

		# strategies:
		self.strat_list = [str(x) if not isinstance(x, tuple) else str(list(x)[0]) for x in input_config.strategies_config[0]]
		self.fw = input_config.strategies_config[1]
		self.logger.info("Initialized Reporter")

	def header(self):
		self.logger.info("Writing header")

		ss = MdFormatter.h1(f"Backtest - {self.name} from {self.begin} to {self.end}")
		ss += MdFormatter.h2("Products:")
		ss += MdFormatter.item_list(self.products_name_list)

		ss += MdFormatter.h2("VolTarget:")
		ss += "Using " + MdFormatter.italic(type(self.size_policy).__name__) + " for Position Sizing\n"
		ss += MdFormatter.item_list(self.size_policy.vol_target.to_list())

		ss += MdFormatter.h2("Strategies:")
		ss += MdFormatter.item_list([f"{w} x {strat}" for w, strat in zip(self.fw.weights, self.strat_list)])

		return ss

	def process_results(self, query_path: str, export_dir: str, raw_results: dict):
		pass
