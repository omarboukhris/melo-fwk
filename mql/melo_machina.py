from melo_fwk.config.melo_books_config import MeloBooksConfig
from melo_fwk.config.product_config import ProductFactory
from melo_fwk.market_data.compo_market_loader import CompositeMarketLoader
from melo_fwk.portfolio.compo_portfolio_mgr import CompositePortfolioManager
from melo_fwk.loggers.global_logger import GlobalLogger

from melo_fwk.config import MeloConfig
from melo_fwk.quantfactory_registry import QuantFlowRegistry

from melo_fwk.utils.generic_config_loader import GenericConfigLoader

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

	def run_process(self, query_path: Path):
		"""
		Note : this will be obsolete once pf aggregation is implemented
			will probably be in a seperate melo process

		Estimators should:
			- Implement the same constructor (see any estimator)
			- Implement a run() method that returns any result

			Reporter associated to the estimator should be able
			to process its result
			TODO: rework reporters with new persistency layer
		"""

		parsed_mql = self.mql_parser.parse_to_json(str(query_path))
		quant_query = parsed_mql["QuantQuery"][0]
		# print(parsed_mql)

		market_mgr = CompositeMarketLoader.from_config(GenericConfigLoader.get_node(CompositeMarketLoader.__name__))
		pf_mgr = CompositePortfolioManager.from_config(GenericConfigLoader.get_node(CompositePortfolioManager.__name__))
		if "Clusters" in quant_query.keys():
			mql_clusters_config = MeloBooksConfig.build_config(pf_mgr, market_mgr, quant_query)
			cluster_estim_ = mql_clusters_config.build_clusters_estimator()
			output = cluster_estim_.run()
			mql_clusters_config.write_report(output, str(query_path.parent))

		else:
			pf = ProductFactory(market_mgr)
			mql_config = MeloConfig.build_config(
				pfactory=pf,
				quant_query_path=query_path,
				quant_query=quant_query
			)

			estimator_obj_ = mql_config.build_estimator()
			output = estimator_obj_.run()

			# ##################################################################################
			# rework this to be parametric
			mql_config.write_report(output, str(query_path.parent))
			mql_config.export_trading_system(pf_mgr)

	def run(self, query_path: Path):
		mql_config = self.mql_parser.parse_to_config(str(query_path))
		estimator_obj_ = mql_config.build_estimator()
		output = estimator_obj_.run()

		mql_config.write_report(output, str(query_path.parent))
		pf_mgr = CompositePortfolioManager.from_config(GenericConfigLoader.get_node(CompositePortfolioManager.__name__))
		mql_config.export_trading_system(pf_mgr)
