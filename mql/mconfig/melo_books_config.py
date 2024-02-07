from dataclasses import dataclass
from typing import List, Dict

from mql.mconfig.common_melo_config import CommonMeloConfig
from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.pfio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.basket.weights import Weights

@dataclass(frozen=True)
class MeloBooksConfig(CommonMeloConfig):
	cluster_names: List[str]
	dependency_map: Dict[str, List[str]]
	weights: Weights
	time_period: List[int]

	pf_mgr: BasePortfolioManager
	market_db: BaseMarketLoader

	def build_trading_systems(self) -> List[BaseTradingSystem]:
		return list(map(self.load_cluster, self.cluster_names))

	def load_cluster(self, cluster_name: str) -> BaseTradingSystem:
		return self.pf_mgr.load_portfolio_config(self.market_db, cluster_name)

