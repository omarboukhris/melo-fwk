import json
import unittest
from pathlib import Path

from mutils.loggers.console_logger import ConsoleLogger
from mutils.loggers.global_logger import GlobalLogger
from melo_fwk.quantfactory_registry import QuantFlowRegistry
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

	def test_decoder(self):
		root_dir = Path(__file__).parent.parent
		templates = {
			# "alloc": root_dir / "mql_data/mql_alloc_optim_template/allocationoptim_example_query_2.sql",
			"var": root_dir / "mql_data/mql_var_template/var_example_query.sql",
			"backtest": root_dir / "mql_data/mql_backtest_template/backtest_example_query.sql",
			"fw_opt": root_dir / "mql_data/mql_forecast_weights_optim/forecastweightsoptim_example_query.sql",
			"vol_target_opt": root_dir / "mql_data/mql_vol_target_optim/posesizeoptim_example_query.sql",
			"clustering": root_dir / "mql_data/mql_clustering_template/clustering_example_query.sql",
			"fast_strat_opt": root_dir / "mql_data/mql_strat_opt_template/fast_stratoptim_example_query.sql",
		}

		for key, mql_query in templates.items():
			raw_parsed_mql = str(self.mql_parser.parse_to_json(str(mql_query))).replace("'", '"')
			assert raw_parsed_mql != ""
			json.loads(raw_parsed_mql, cls=MqlDecoder)


if __name__ == "__main__":
	unittest.main()
