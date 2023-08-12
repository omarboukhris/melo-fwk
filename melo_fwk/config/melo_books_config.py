from dataclasses import dataclass
from typing import List, Tuple, Type

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.strat_basket import StratBasket
from melo_fwk.config.common_melo_config import CommonMeloConfig
from melo_fwk.config.mql_dict import MqlDict
from melo_fwk.config.estimator_config import EstimatorConfigBuilder
from melo_fwk.estimators.pf_allocation_estimator import PFAllocationEstimator
from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.portfolio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.pose_size import BaseSizePolicy
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.utils.weights import Weights

@dataclass(frozen=True)
class MeloBooksConfig(CommonMeloConfig):
	cluster_names: List[str]
	product_baskets: List[ProductBasket]
	strats_list: List[StratBasket]
	pose_size_list: List[BaseSizePolicy]
	weights: Weights
	time_period: List[int]
	estimator_config_: Tuple[Type[PFAllocationEstimator], dict]

	def __post_init__(self):
		assert len(self.product_baskets) == len(self.strats_list), \
			f"len product != strat ({len(self.product_baskets)} != {len(self.strats_list)})"
		assert len(self.product_baskets) == len(self.pose_size_list), \
			f"len product != size_policy ({len(self.product_baskets)} != {len(self.pose_size_list)})"

	def build_trading_systems(self) -> List[BaseTradingSystem]:
		return [
			TradingSystem(
				name=name,
				product_basket=p_basket,
				strat_basket=s_basket,
				size_policy=size_policy)
			for name, p_basket, s_basket, size_policy in zip(
				self.cluster_names, self.product_baskets, self.strats_list, self.pose_size_list)
		]

	@staticmethod
	def build_config(pf_mgr: BasePortfolioManager, market_db: BaseMarketLoader, quant_query: dict):
		time_period, clusters, weights = MeloBooksConfig.load_clusters(pf_mgr, market_db, quant_query)
		return MeloBooksConfig(
			name=quant_query.strip_single("QueryName"),
			cluster_names=[c.name for c in clusters],
			product_baskets=[c.product_basket for c in clusters],
			strats_list=[c.strat_basket for c in clusters],
			pose_size_list=[c.size_policy for c in clusters],
			reporter_class_=EstimatorConfigBuilder.get_reporter(quant_query),
			estimator_config_=EstimatorConfigBuilder.build_estimator(quant_query),
			time_period=time_period,
			weights=weights,
		)

	@staticmethod
	def load_clusters(
		pf_mgr: BasePortfolioManager,
		market_db: BaseMarketLoader,
		quant_query: dict
	) -> Tuple[List[int], List[BaseTradingSystem], Weights]:

		mql_dict = MqlDict(quant_query)
		clusters_mql_dict = mql_dict.strip_single("Clusters")
		clusters_name = clusters_mql_dict.parse_list("AlphanumList")
		clusters_weights = clusters_mql_dict.parse_num_list("WeightsList")
		clusters_divmult = float(mql_dict.strip_single("DivMult"))
		time_period_mql_dict = clusters_mql_dict.strip_single("TimePeriod")
		time_period = time_period_mql_dict.parse_num_list("timeperiod", default=[0, 0], type_=int)

		weights = Weights(
			weights=clusters_weights,
			divmult=clusters_divmult
		)

		clusters = [
			pf_mgr.load_portfolio_config(market_db, c_name)
			for c_name in clusters_name
		]
		return time_period, clusters, weights

	def build_clusters_estimator(self):
		return self.estimator_config_[0](
			estimator_params=self.estimator_config_[1],
			time_period=self.time_period,
			trading_syst_list=self.build_trading_systems(),
			weights=self.weights,
		)
