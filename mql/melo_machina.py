from melo_fwk.pfio.compo_portfolio_mgr import CompositePortfolioManager
from mutils.loggers.global_logger import GlobalLogger

from melo_fwk.quantfactory_registry import QuantFlowRegistry

from mutils.generic_config_loader import GenericConfigLoader

from mql.mql_parser import MqlParser

from pathlib import Path


class MeloMachina:

	def __init__(self, config: Path, loggers: list):
		# setup config
		GenericConfigLoader.setup(str(config))
		# setup logger
		GlobalLogger.set_loggers(loggers)
		# register melo components in factory
		# registration comes after config loading
		# otherwise product factory would not be initialized
		QuantFlowRegistry.register_all()
		# setup mql parsers
		self.mql_parser = MqlParser()

	def run(self, query_path: Path):
		"""
		Estimators should:
			- Implement the same constructor (see any estimator)
			- Implement a run() method that returns any result

			Reporter associated to the estimator should be able
			to process its result
			TODO: rework reporters with new persistency layer
		"""
		mql_config = self.mql_parser.parse_to_config(str(query_path))
		estimator_obj_ = mql_config.build_estimator()
		output = estimator_obj_.run()

		mql_config.write_report(output, str(query_path.parent))
		pf_mgr = CompositePortfolioManager.from_config(GenericConfigLoader.get_node(CompositePortfolioManager.__name__))
		mql_config.export_trading_system(pf_mgr)
