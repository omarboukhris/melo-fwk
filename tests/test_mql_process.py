import unittest
from pathlib import Path

from mutils.loggers.console_logger import ConsoleLogger
from mql.melo_machina import MeloMachina


class MqlUnitTests(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = Path(__file__).parent / "rc/config.json"
		self.loggers = [ConsoleLogger]
		root_dir = Path(__file__).parent.parent
		self.templates = {
			# "alloc2": root_dir / "mql_data/mql_alloc_optim_template/allocationoptim_example_query_2.sql",
			# "alloc": root_dir / "mql_data/mql_alloc_optim_template/allocationoptim_example_query.sql",
			"var": root_dir / "mql_data/mql_var_template/var_example_query.sql",
			"backtest": root_dir / "mql_data/mql_backtest_template/backtest_example_query.sql",
			"fw_opt": root_dir / "mql_data/mql_forecast_weights_optim/forecastweightsoptim_example_query.sql",
			"vol_target_opt": root_dir / "mql_data/mql_vol_target_optim/posesizeoptim_example_query.sql",
			"clustering": root_dir / "mql_data/mql_clustering_template/clustering_example_query.sql",
			"fast_strat_opt": root_dir / "mql_data/mql_strat_opt_template/fast_stratoptim_example_query.sql",
		}

	def test_mql_process(self):
		mm = MeloMachina(config=self.config, loggers=self.loggers)

		for key, mql_query in self.templates.items():
			print(42*"=" + key + 42*"=")
			mm.run(query_path=mql_query)


if __name__ == "__main__":
	unittest.main()
