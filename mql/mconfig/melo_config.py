from typing import List, Type, Tuple, Dict, Union

from mql.mconfig.common_melo_config import CommonMeloConfig
from mql.mconfig.strat_config import StratConfigRegistry
from melo_fwk.pfio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.estimators.base_estimator import MeloBaseEstimator
from melo_fwk.pose_size import BaseSizePolicy

from dataclasses import dataclass, asdict

from melo_fwk.strategies import BaseStrategy
from melo_fwk.basket.weights import Weights


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
		return asdict(self)

	def __str__(self):
		return str(self.asdict())

	def export_trading_system(self, pf_mgr: BasePortfolioManager):
		"""should it take an exportMgr object as param for export ??"""
		if self.export_name is not None:
			# do the stuff here
			pf_mgr.save_portfolio_config(self.name, self.build_estimator().build_trading_system_cluster())
