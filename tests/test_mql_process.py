import unittest

from melo_fwk.config.melo_clusters_config import MeloClustersConfig
from melo_fwk.market_data.compo_market_loader import CompositeMarketLoader
from melo_fwk.portfolio.compo_portfolio_mgr import CompositePortfolioManager
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.loggers.console_logger import ConsoleLogger

from melo_fwk.config import MeloConfig

from melo_fwk import quantfactory_registry
from melo_fwk.utils.generic_config_loader import GenericConfigLoader

from mql.mql_parser import MqlParser

from pathlib import Path


class MeloMachina:

	def __init__(self, config: Path, loggers: list):
		# setup config
		GenericConfigLoader.setup(str(config))
		# setup logger
		GlobalLogger.set_loggers(loggers)
		# setup mql parser
		self.mql_parser = MqlParser()
		# register melo components in factory
		quantfactory_registry.register_all()

	def run_mql_process(self, mql_query_path: Path):
		"""
		Estimators should:
			- Implement the same constructor (see any estimator)
			- Implement a run() method that returns any result
		Note:
			Reporter associated to the estimator should be able
			to process its result
			TODO: rework reporters with new persistency layer
		"""

		parsed_mql = self.mql_parser.parse_to_json(str(mql_query_path))
		quant_query = parsed_mql["QuantQuery"][0]
		# print(parsed_mql)

		if "Clusters" in quant_query.keys():
			pf_mgr = CompositePortfolioManager.from_config(GenericConfigLoader.get_node(CompositePortfolioManager.__name__))
			market_mgr = CompositeMarketLoader.from_config(GenericConfigLoader.get_node(CompositeMarketLoader.__name__))
			mql_clusters_config = MeloClustersConfig.build_config(pf_mgr, market_mgr, quant_query)
			cluster_estim_ = mql_clusters_config.build_clusters_estimator()
			output = cluster_estim_.run()
			mql_clusters_config.write_report(output, str(mql_query_path.parent))

		else:
			mql_config = MeloConfig.build_config(
				quant_query_path=mql_query_path,
				quant_query=quant_query
			)
			# print(mql_config)

			estimator_obj_ = mql_config.build_estimator()
			output = estimator_obj_.run()
			# print(output)
			# ##################################################################################
			mql_config.write_report(output, str(mql_query_path.parent))

			pf_mgr = CompositePortfolioManager.from_config(GenericConfigLoader.get_node(CompositePortfolioManager.__name__))
			mql_config.export_trading_system(pf_mgr)


class MqlUnitTests(unittest.TestCase):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.config = Path(__file__).parent / "rc/config.json"
		self.loggers = [ConsoleLogger]

	def test_mql_process(self):

		root_dir = Path(__file__).parent.parent
		templates = {
			"var": root_dir / "mql_data/mql_var_template/var_example_query.sql",
			"alloc": root_dir / "mql_data/mql_alloc_optim_template/allocationoptim_example_query.sql",
			"backtest": root_dir / "mql_data/mql_backtest_template/backtest_example_query.sql",
			"fw_opt": root_dir / "mql_data/mql_forecast_weights_optim/forecastweightsoptim_example_query.sql",
			"vol_target_opt": root_dir / "mql_data/mql_vol_target_optim/posesizeoptim_example_query.sql",
			"clustering": root_dir / "mql_data/mql_clustering_template/clustering_example_query.sql",
			"fast_strat_opt": root_dir / "mql_data/mql_strat_opt_template/fast_stratoptim_example_query.sql",
		}
		# still missing :
		# alloc opt

		# set loggers
		mm = MeloMachina(config=self.config, loggers=self.loggers)

		for key, mql_query in templates.items():
			print(42*"=" + key + 42*"=")
			mm.run_mql_process(mql_query_path=mql_query)


if __name__ == "__main__":
	unittest.main()
