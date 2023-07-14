import json
from pathlib import Path

from melo_fwk.config.melo_books_config import MeloBooksConfig
from melo_fwk.utils.generic_config_loader import GenericConfigLoader
from melo_fwk.market_data.compo_market_loader import CompositeMarketLoader
from melo_fwk.config.product_config import ProductFactory
from melo_fwk.config import MeloConfig
from melo_fwk.config.config_helper import ConfigBuilderHelper
from melo_fwk.config.estimator_config import EstimatorConfigBuilder
from melo_fwk.config.pose_size_config import SizePolicyConfigBuilder
from melo_fwk.config.strat_config import StrategyConfigBuilder, StratConfigRegistry

from melo_fwk.basket.strat_basket import StratBasket

class MqlDecoder(json.JSONDecoder):
	def __init__(self, *args, **kwargs):
		json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
		self.strat_config_point = Path(GenericConfigLoader.get_node("strat_config_points", "strat_config_points"))
		market_mgr = CompositeMarketLoader.from_config(GenericConfigLoader.get_node(CompositeMarketLoader.__name__))
		self.pfactory = ProductFactory(market_mgr)

	def object_hook(self, obj: dict):

		if len(obj.keys()) != 1:
			return obj
		if list(obj.keys())[0] != "QuantQuery":
			return obj
		quant_query = obj["QuantQuery"][0]

		if "Clusters" in quant_query.keys():
			return self.build_melo_books_config(quant_query)
		else:
			return self.build_melo_config(quant_query)

	def build_melo_config(self, quant_query):
		estimator_class_, estimator_params_ = EstimatorConfigBuilder.build_estimator(quant_query)
		strat_config_registry = StratConfigRegistry.build_registry(str(self.strat_config_point))
		return MeloConfig(
			name=ConfigBuilderHelper.strip_single(quant_query, "QueryName"),
			products_config=self.pfactory.build_products(quant_query),
			size_policy=SizePolicyConfigBuilder.build_size_policy(quant_query),
			strat_config_registry=strat_config_registry,
			strategies_config=StrategyConfigBuilder.build_strategy(quant_query, strat_config_registry),
			estimator_class_=estimator_class_,
			estimator_params_=estimator_params_,
			reporter_class_=EstimatorConfigBuilder.get_reporter(quant_query),
			export_name=EstimatorConfigBuilder.get_export_name(quant_query)
		)

	def build_melo_books_config(self, quant_query: dict):

		time_period, clusters, weights = MeloBooksConfig.load_clusters(pf_mgr, market_db, quant_query)
		return MeloBooksConfig(
			name=ConfigBuilderHelper.strip_single(quant_query, "QueryName"),
			cluster_names=[c.name for c in clusters],
			product_baskets=[c.product_basket for c in clusters],
			strats_list=[c.strat_basket for c in clusters],
			pose_size_list=[c.size_policy for c in clusters],
			reporter_class_=EstimatorConfigBuilder.get_reporter(quant_query),
			estimator_config_=EstimatorConfigBuilder.build_estimator(quant_query),
			time_period=time_period,
			weights=weights,
		)

