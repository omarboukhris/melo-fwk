import json
import unittest
from pathlib import Path

import mepo.books as mepo
from mepo import books
from mql.melo_machina import MeloMachina
from mutils.loggers.console_logger import ConsoleLogger
from mutils.loggers.global_logger import GlobalLogger
from mutils.quantfactory_registry import QuantFlowRegistry
from mutils.generic_config_loader import GenericConfigLoader
from mql.mql_decoder import MqlDecoder
from mql.mql_parser import MqlParser


class MqlDecoderUnitTests(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		GenericConfigLoader.setup(str(Path(__file__).parent / "rc/config.json"))
		GlobalLogger.set_loggers([ConsoleLogger])
		QuantFlowRegistry.register_all()
		self.mql_parser = MqlParser()
		self.config = Path(__file__).parent / "rc/config.json"
		self.loggers = [ConsoleLogger]
		self.templates = [
			'mepo.generic_strat_optim_example',
			'mepo.products_cluster_example',
			'mepo.inf_vol_target_example',
			'mepo.fw_optim_example',
			'mepo.simple_book_backtest_example',
		]
		self.processes = [
			"StratOptimEstimator",
			"ClustersEstimator",
			"VolTargetEstimator",
			"ForecastWeightsEstimator",
			"BacktestEstimator",
		]

	def test_mepo(self):
		for key in self.templates:
			mql_query = mepo.auto_books.get(key)
			raw_parsed_mql = str(self.mql_parser.parse_to_json(str(mql_query))).replace("'", '"')
			assert raw_parsed_mql != ""
			json.loads(raw_parsed_mql, cls=MqlDecoder)

	def test_mepo_process(self):
		mm = MeloMachina(config=self.config, loggers=self.loggers)

		for template, process in zip(self.templates, self.processes):
			print(42*"=" + f"{template}>>{process}" + 42*"=")
			book_path = books.auto_books.get(template)
			mm.run(
				export_path=str(Path(__file__).parent / "rc"),
				book_path=book_path,
				process=process,
				config="estim.default",
			)


if __name__ == "__main__":
	unittest.main()
