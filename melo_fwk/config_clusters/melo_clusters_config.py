from dataclasses import dataclass
from typing import List

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.start_basket import StratBasket
from melo_fwk.config_clusters.pose_size_list_config import SizePolicyListConfigBuilder
from melo_fwk.config_clusters.product_basket_config import ProductBasketConfigBuilder
from melo_fwk.config_clusters.strat_basket_config import StratBasketConfigBuilder
from melo_fwk.pose_size import BaseSizePolicy
from melo_fwk.trading_systems import TradingSystem


@dataclass(frozen=True)
class MeloClustersConfig:
	product_baskets: List[ProductBasket]
	strats_list: List[StratBasket]
	pose_size_list: List[BaseSizePolicy]
	# add estimator

	def __post_init__(self):
		assert len(self.product_baskets) == len(self.strats_list), \
			f"len product != strat ({len(self.product_baskets)} != {len(self.strats_list)})"
		assert len(self.product_baskets) == len(self.pose_size_list), \
			f"len product != size_policy ({len(self.product_baskets)} != {len(self.pose_size_list)})"

	def build_trading_systems(self):
		return [
			TradingSystem(product_basket=p_basket, strat_basket=s_basket, size_policy=size_policy)
			for p_basket, s_basket, size_policy in zip(self.product_baskets, self.strats_list, self.pose_size_list)
		]

	@staticmethod
	def build_config(quant_query: dict):
		return MeloClustersConfig(
			product_baskets=ProductBasketConfigBuilder.build_product_baskets(quant_query),
			strats_list=StratBasketConfigBuilder.build_strat_baskets(quant_query),
			pose_size_list=SizePolicyListConfigBuilder.build_size_list(quant_query),
		)

	def build_clusters_estimator(self):
		raise NotImplemented

