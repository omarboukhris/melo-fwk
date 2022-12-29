import unittest

from melo_fwk.config_clusters.melo_clusters_config import MeloClustersConfig
from melo_fwk.db.portfolio.compo_portfolio_mgr import CompositePortfolioManager
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.loggers.console_logger import ConsoleLogger

from melo_fwk.config import MeloConfig

from melo_fwk import quantfactory_registry

from mql.mql_parser import MqlParser

from pathlib import Path

import uuid

def run_mql_process(mql_query_path: Path):
	"""
	Estimators should:
		- Implement the same constructor (see any estimator)
		- Implement a run() method that returns any result
	Note:
		Reporter associated to the estimator should be able
		to process its result

	TODO:
		Add estimator config load from toml file
		+ default config load from some assets/folder
	"""

	mql_parser = MqlParser()
	parsed_mql = mql_parser.parse_to_json(str(mql_query_path))
	quant_query = parsed_mql["QuantQuery"][0]
	# print(parsed_mql)

	if "Clusters" in quant_query.keys():
		mql_clusters_config = MeloClustersConfig.build_config(quant_query=quant_query)
		cluster_estim_ = mql_clusters_config.build_clusters_estimator()
		output = cluster_estim_.run()
		mql_clusters_config.write_report(output, str(mql_query_path.parent))
		raise NotImplemented()

	else:
		mql_config = MeloConfig.build_config(
			quant_query_path=mql_query_path,
			quant_query=quant_query
		)
		# print(mql_config)

		estimator_obj_ = mql_config.build_estimator()
		output = estimator_obj_.run()
		# print(output)

		mql_config.write_report(output, str(mql_query_path.parent))

		pf_mgr = CompositePortfolioManager.with_mongo_second(
			dburl="mongodb://localhost:27017/",
			fallback_path="/home/omar/PycharmProjects/melo-fwk/melo_fwk/db/portfolio/assets"
		)
		mql_config.export_trading_system(pf_mgr, str(uuid.uuid4()))


class MqlUnitTests(unittest.TestCase):

	def test_mql_process(self):

		templates = {
			# "alloc": Path(__file__).parent.parent / "mql/data/mql_alloc_optim_template/allocationoptim_example_query.sql",
			"backtest": Path(__file__).parent.parent / "mql/data/mql_backtest_template/backtest_example_query.sql",
			"fw_opt": Path(__file__).parent.parent / "mql/data/mql_forecast_weights_optim/forecastweightsoptim_example_query.sql",
			"vol_target_opt": Path(__file__).parent.parent / "mql/data/mql_vol_target_optim/posesizeoptim_example_query.sql",
			"clustering": Path(__file__).parent.parent / "mql/data/mql_clustering_template/clustering_example_query.sql",
			# "fast_strat_opt": Path(__file__).parent.parent / "mql/data/mql_strat_opt_template/fast_stratoptim_example_query.sql",
		}
		# still missing :
		# alloc opt

		# set loggers
		GlobalLogger.set_loggers([ConsoleLogger])

		# register melo components in factory
		quantfactory_registry.register_all()

		for key, mql_query in templates.items():
			print(42*"=" + key + 42*"=")
			run_mql_process(mql_query_path=mql_query)


if __name__ == "__main__":
	unittest.main()
