from typing import List, Type, Tuple, Dict, Union

from melo_fwk.config.common_melo_config import CommonMeloConfig
from melo_fwk.config.config_helper import ConfigBuilderHelper
from melo_fwk.config.product_config import ProductFactory
from melo_fwk.config.strat_config import StratConfigRegistry, StrategyConfigBuilder
from melo_fwk.config.pose_size_config import SizePolicyConfigBuilder
from melo_fwk.config.estimator_config import EstimatorConfigBuilder
from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.portfolio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.pose_size import BaseSizePolicy

from pathlib import Path

from dataclasses import dataclass

from melo_fwk.strategies import BaseStrategy
from melo_fwk.utils.generic_config_loader import GenericConfigLoader
from melo_fwk.utils.weights import Weights


@dataclass(frozen=True)
class MeloConfig(CommonMeloConfig):
	# {prod_name: Product}, start..end
	products_config: Tuple[dict, List[int]]
	size_policy: BaseSizePolicy
	strat_config_registry: StratConfigRegistry
	# (list(strats OR tuple(type(strat), param)), fw)
	strategies_config: Tuple[List[Union[BaseStrategy, Tuple[Type[BaseStrategy], Dict]]], Weights]
	# (estimator, **params)
	estimator_class_: Type[MeloBaseEstimator]
	estimator_params_: dict
	export_name: str

	@staticmethod
	def build_config(pfactory: ProductFactory, quant_query_path: Path, quant_query: dict):
		"""
		Should rework into config builder factory
		ex: parse strat vs strat metadata

		:param pfactory:
		:param quant_query_path:
		:param quant_query:
		"""
		strat_config_path = GenericConfigLoader.get_node(
			"strat_config_points", str(quant_query_path.parent / "strat_config_points"))
		strat_config_registry = StratConfigRegistry.build_registry(strat_config_path)
		estimator_class_, estimator_params_ = EstimatorConfigBuilder.build_estimator(quant_query)
		return MeloConfig(
			name=ConfigBuilderHelper.strip_single(quant_query, "QueryName"),
			products_config=pfactory.build_products(quant_query),
			size_policy=SizePolicyConfigBuilder.build_size_policy(quant_query),
			strat_config_registry=strat_config_registry,
			strategies_config=StrategyConfigBuilder.build_strategy(quant_query, strat_config_registry),
			estimator_class_=estimator_class_,
			estimator_params_=estimator_params_,
			reporter_class_=EstimatorConfigBuilder.get_reporter(quant_query),
			export_name=EstimatorConfigBuilder.get_export_name(quant_query)
		)

	def build_estimator(self):
		return self.estimator_class_(
			products=self.products_config[0],
			time_period=self.products_config[1],
			strategies=self.strategies_config[0],
			forecast_weights=self.strategies_config[1],
			size_policy=self.size_policy,
			estimator_params=self.estimator_params_
		)

	def asdict(self):
		return {
			"products_config": self.products_config,
			"size_policy": self.size_policy,
			"strat_config_registry": self.strat_config_registry,
			"strategies_config": self.strategies_config,
			"estimator_class_": self.estimator_class_,
			"estimator_params_": self.estimator_params_,
			"reporter_class_": self.reporter_class_,
			"export_name": self.export_name,
		}

	def __str__(self):
		return str(self.asdict())

	def export_trading_system(self, pf_mgr: BasePortfolioManager):
		"""should it take an exportMgr object as param for export ??"""
		if self.export_name is not None:
			# do the stuff here
			pf_mgr.save_portfolio_config(self.name, self.build_estimator().build_trading_system_cluster())
