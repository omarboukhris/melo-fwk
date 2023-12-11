from dataclasses import dataclass
from typing import List, Tuple, Type, Dict

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.strat_basket import StratBasket
from mql.mconfig.common_melo_config import CommonMeloConfig
from mql.mconfig.mql_dict import MqlDict
from mql.mconfig.estimator_config import EstimatorConfigBuilder
from melo_fwk.estimators.pf_allocation_estimator import PFAllocationEstimator
from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.pfio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.pose_size import BaseSizePolicy
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.basket.weights import Weights

@dataclass(frozen=True)
class MeloBooksConfig(CommonMeloConfig):
	cluster_names: List[str]
	dependency_map: Dict[str, List[str]]
	weights: Weights
	time_period: List[int]
	estimator_config_: Tuple[Type[PFAllocationEstimator], dict]

	pf_mgr: BasePortfolioManager
	market_db: BaseMarketLoader

	def build_trading_systems(self) -> List[BaseTradingSystem]:
		return list(map(self.load_cluster, self.cluster_names))

	def load_cluster(self, cluster_name: str) -> BaseTradingSystem:
		return self.pf_mgr.load_portfolio_config(self.market_db, cluster_name)


	def build_clusters_estimator(self):
		"""
		Rework this after refactoring books estimators/aggregator
		should be lazy, use load_cluster  instead of build training_systems
		"""
		return self.estimator_config_[0](
			estimator_params=self.estimator_config_[1],
			time_period=self.time_period,
			trading_syst_list=self.build_trading_systems(),
			weights=self.weights,
		)
