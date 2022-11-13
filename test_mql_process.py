from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.loggers.console_logger import ConsoleLogger

from melo_fwk.config import (
	ConfigBuilderHelper,
	MeloConfig
)
from melo_fwk import quantfactory_registry

from mql.mql_parser import MqlParser

from pathlib import Path


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
	quant_query = ConfigBuilderHelper.strip_single(parsed_mql, "QuantQuery")
	# print(parsed_mql)

	mql_config = MeloConfig.build(
		quant_query_path=mql_query_path,
		quant_query=quant_query
	)
	# print(mql_config)

	estimator_obj_ = mql_config.build_estimator()
	output = estimator_obj_.run()
	# print(output)

	mql_config.write_report(output, str(mql_query_path.parent))



if __name__ == "__main__":

	templates = {
		# "backtest": Path(__file__).parent / "mql/data/mql_backtest_template/backtest_example_query.sql",
		# "fw_opt": Path(__file__).parent / "mql/data/mql_forecast_weights_optim/forecastweightsoptim_example_query.sql",
		# "vol_target_opt": Path(__file__).parent / "mql/data/mql_vol_target_optim/posesizeoptim_example_query.sql",
		# "clustering": Path(__file__).parent / "mql/data/mql_clustering_template/clustering_example_query.sql",
		"fast_strat_opt": Path(__file__).parent / "mql/data/mql_strat_opt_template/fast_stratoptim_example_query.sql",
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

