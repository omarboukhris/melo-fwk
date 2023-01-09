from dataclasses import dataclass
from typing import List, Tuple, Type

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.strat_basket import StratBasket
from melo_fwk.config.common_melo_config import CommonMeloConfig
from melo_fwk.config.config_helper import ConfigBuilderHelper
from melo_fwk.config.estimator_config import EstimatorConfigBuilder
from melo_fwk.estimators_clusters.base_cluster_estimator import BaseClusterEstimator
from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.portfolio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.pose_size import BaseSizePolicy
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.utils.weights import Weights

@dataclass(frozen=True)
class MeloClustersConfig(CommonMeloConfig):
	product_baskets: List[ProductBasket]
	strats_list: List[StratBasket]
	pose_size_list: List[BaseSizePolicy]
	weights: Weights
	estimator_config_: Tuple[Type[BaseClusterEstimator], List[str]]

	def __post_init__(self):
		assert len(self.product_baskets) == len(self.strats_list), \
			f"len product != strat ({len(self.product_baskets)} != {len(self.strats_list)})"
		assert len(self.product_baskets) == len(self.pose_size_list), \
			f"len product != size_policy ({len(self.product_baskets)} != {len(self.pose_size_list)})"

	def build_trading_systems(self) -> List[BaseTradingSystem]:
		return [
			TradingSystem(product_basket=p_basket, strat_basket=s_basket, size_policy=size_policy)
			for p_basket, s_basket, size_policy in zip(self.product_baskets, self.strats_list, self.pose_size_list)
		]

	@staticmethod
	def build_config(pf_mgr: BasePortfolioManager, market_db: BaseMarketLoader, quant_query: dict):
		clusters, weights = MeloClustersConfig.load_clusters(pf_mgr, market_db, quant_query)
		return MeloClustersConfig(
			name=ConfigBuilderHelper.strip_single(quant_query, "QueryName"),
			product_baskets=[c.product_basket for c in clusters],
			strats_list=[c.strat_basket for c in clusters],
			pose_size_list=[c.size_policy for c in clusters],
			reporter_class_=EstimatorConfigBuilder.get_reporter(quant_query),
			estimator_config_=EstimatorConfigBuilder.build_estimator(quant_query),
			weights=weights,
		)

	@staticmethod
	def load_clusters(
		pf_mgr: BasePortfolioManager,
		market_db: BaseMarketLoader,
		quant_query: dict
	) -> Tuple[List[BaseTradingSystem], Weights]:

		clusters_dict = ConfigBuilderHelper.strip_single(quant_query, "Clusters")
		clusters_name = [s.strip() for s in ConfigBuilderHelper.strip_single(clusters_dict, "AlphanumList").split(",")]
		clusters_weights = [float(s) for s in ConfigBuilderHelper.strip_single(clusters_dict, "WeightsList").split(",")]
		clusters_divmult = float(ConfigBuilderHelper.strip_single(clusters_dict, "DivMult"))

		weights = Weights(
			weights=clusters_weights,
			divmult=clusters_divmult
		)

		clusters = [
			pf_mgr.load_portfolio_config(market_db, c_name)
			for c_name in clusters_name
		]
		return clusters, weights

	def build_clusters_estimator(self):
		return self.estimator_config_[0](
			estimator_params=self.estimator_config_[1],
			trading_syst_list=self.build_trading_systems(),
			weights=self.weights,
		)
