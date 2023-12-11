import json
import re
from functools import reduce
from pathlib import Path

from melo_fwk.basket.weights import Weights
from mql.mconfig.melo_books_config import MeloBooksConfig
from melo_fwk.pfio.compo_portfolio_mgr import CompositePortfolioManager
from mutils.generic_config_loader import GenericConfigLoader
from melo_fwk.market_data.compo_market_loader import CompositeMarketLoader
from mql.mconfig.pose_size_config import SizePolicyConfigBuilder
from mql.mconfig.product_config import ProductFactory
from mql.mconfig import MeloConfig
from mql.mconfig.mql_dict import MqlDict
from mql.mconfig.estimator_config import EstimatorConfigBuilder
from mql.mconfig.strat_config import StratConfigRegistry, StrategyConfigBuilder


class MqlDecoder(json.JSONDecoder):
	def __init__(self, *args, **kwargs):
		json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
		self.strat_config_point = Path(GenericConfigLoader.get_node("strat_config_points", "strat_config_points"))
		self.market_mgr = CompositeMarketLoader.from_config(GenericConfigLoader.get_node(CompositeMarketLoader.__name__))
		pf_mgr = CompositePortfolioManager.from_config(GenericConfigLoader.get_node(CompositePortfolioManager.__name__))
		self.pfactory = ProductFactory(self.market_mgr)
		self.pfolio = pf_mgr

	def object_hook(self, obj: dict):

		if len(obj.keys()) != 1 or list(obj.keys())[0] != "QuantQuery":
			return obj
		quant_query = obj["QuantQuery"][0]

		if "Clusters" in quant_query.keys():
			return self.build_melo_books_config(quant_query)
		else:
			return self.build_melo_config(quant_query)

	def build_melo_config(self, quant_query: dict):
		mql_dict = MqlDict(quant_query)
		estimator_class_, estimator_params_ = EstimatorConfigBuilder.build_estimator(mql_dict)
		strat_config_registry = StratConfigRegistry.build_registry(str(self.strat_config_point))
		return MeloConfig(
			name=mql_dict.get_node("QueryName"),
			products_config=self.pfactory.build_products(mql_dict),
			size_policy=SizePolicyConfigBuilder.build_size_policy(mql_dict),
			strategies_config=StrategyConfigBuilder.build_strategy(mql_dict, strat_config_registry),
			estimator_class_=estimator_class_,
			estimator_params_=estimator_params_,
			reporter_class_=EstimatorConfigBuilder.get_reporter(mql_dict),
			export_name=EstimatorConfigBuilder.get_export_name(mql_dict)
		)

	def build_unweighted_book(self, books_mql_dict: MqlDict):
		books_dep_map = {
			node_name: re.sub(r"( |,)", " ", node_list_str).split()
			for node_list_str, node_name in zip(*books_mql_dict.values())
		}

		# sanity check
		nodes_k = set(books_dep_map.keys())
		nodes_v = set(reduce(lambda a, b: a+b, books_dep_map.values(), []))
		terminal_nodes = nodes_v - nodes_k
		# check that missing ones are in books database, otherwise node is undefined
		missing = {m for m in terminal_nodes if not self.pfolio.book_exists(m)}
		assert len(missing) == 0, \
			f"(Scheduler) Missing nodes in process dependency map {missing}"

		return books_dep_map, terminal_nodes

	def build_melo_books_config(self, quant_query: dict):
		# time_period, clusters, weights = MeloBooksConfig.load_clusters(pf_mgr, market_db, quant_query)
		mql_dict = MqlDict(quant_query)
		query_name = mql_dict.get_node("QueryName")
		estimator_config_ = EstimatorConfigBuilder.build_estimator(mql_dict)
		clusters_mql_dict = mql_dict.get_node("Clusters")
		time_period_mql_dict = clusters_mql_dict.get_node("TimePeriod")
		time_period = time_period_mql_dict.parse_num_list("timeperiod", default=[0, 0], type_=int)
		books_mql_dict = clusters_mql_dict.get_node("Books")
		books_dep_map, terminal_nodes = self.build_unweighted_book(books_mql_dict)
		weights = Weights(weights=[1.] * len(terminal_nodes), divmult=1.)

		""" Store lazily, launch multiprocesses and aggregate
		All Estimators should have book aggregators
		Estimators should export to db (use mongo) to simplify aggregation
		think about weighted books and processes (branch here ??)
		"""
		return MeloBooksConfig(
			name=query_name,
			cluster_names=list(terminal_nodes),
			dependency_map=books_dep_map,
			reporter_class_=EstimatorConfigBuilder.get_reporter(mql_dict),
			weights=weights,  # uniform weights for unweighted
			time_period=time_period,
			estimator_config_=estimator_config_,

			pf_mgr=self.pfolio,
			market_db=self.market_mgr
		)

