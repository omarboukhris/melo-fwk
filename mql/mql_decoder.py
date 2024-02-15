import json

from mutils.generic_config_loader import GenericConfigLoader
from melo_fwk.market_data.compo_market_loader import CompositeMarketLoader
from mql.mconfig.pose_size_config import SizePolicyConfigBuilder
from mql.mconfig.product_config import ProductFactory
from mql.mconfig import MeloConfig
from mql.mconfig.mql_dict import MqlDict
from mql.mconfig.strat_config import StrategyConfigBuilder


class MqlDecoder(json.JSONDecoder):
	def __init__(self, *args, **kwargs):
		json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)
		self.market_mgr = CompositeMarketLoader.from_config(GenericConfigLoader.get_node(CompositeMarketLoader.__name__))
		self.pfactory = ProductFactory(self.market_mgr)

	def object_hook(self, obj: dict):

		if len(obj.keys()) != 1 or list(obj.keys())[0] != "QuantQuery":
			return obj

		quant_query = obj["QuantQuery"][0]
		mql_dict = MqlDict(quant_query)
		return MeloConfig(
			name=mql_dict.get_node("QueryName"),
			products_config=self.pfactory.build_products(mql_dict),
			size_policy=SizePolicyConfigBuilder.build_size_policy(mql_dict),
			strategies_config=StrategyConfigBuilder.build_strategy(mql_dict),
		)
