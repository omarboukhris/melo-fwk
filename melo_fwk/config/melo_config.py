
from melo_fwk.config.product_config import ProductConfigBuilder
from melo_fwk.config.strat_config import StratConfigRegistry, StrategyConfigBuilder
from melo_fwk.config.pose_size_config import SizePolicyConfigBuilder, VolTargetConfigBuilder
from melo_fwk.config.estimator_config import EstimatorConfigBuilder

from melo_fwk.position_size_policies.vol_target import VolTarget

from pathlib import Path

from dataclasses import dataclass

@dataclass(frozen=True)
class MeloConfig:
	products_config: tuple  # (product[], start..end)
	size_policy_class_: callable  # BaseSizePolicy
	vol_target: VolTarget
	strat_config_registry: StratConfigRegistry
	strategies_config: tuple  # (strategy[], fw[])
	estimator_config_: tuple  # (estimator, estimator_param[])

	@staticmethod
	def build(quant_query_path: Path, quant_query: dict):
		"""
		Should rework into config builder factory
		ex: parse strat vs strat metadata

		:param quant_query_path:
		:param quant_query:
		"""
		strat_config_registry = StratConfigRegistry.build_registry(str(quant_query_path.parent))
		return MeloConfig(
			products_config=ProductConfigBuilder.build_products(quant_query),
			size_policy_class_=SizePolicyConfigBuilder.build_size_policy(quant_query),
			vol_target=VolTargetConfigBuilder.build_vol_target(quant_query),
			strat_config_registry=strat_config_registry,
			strategies_config=StrategyConfigBuilder.build_strategy(quant_query, strat_config_registry),
			estimator_config_=EstimatorConfigBuilder.build_estimator(quant_query),
		)

	def build_estimator(self):
		return self.estimator_config_[0](
			products=self.products_config[0],
			time_period=self.products_config[1],
			strategies=self.strategies_config[0],
			forecast_weights=self.strategies_config[1],
			vol_target=self.vol_target,
			size_policy_class_=self.size_policy_class_,
			estimator_params=self.estimator_config_[1]
		)

	def asdict(self):
		return {
			"products_config": self.products_config,
			"size_policy_class_": self.size_policy_class_,
			"vol_target": self.vol_target,
			"strat_config_registry": self.strat_config_registry,
			"strategies_config": self.strategies_config,
			"estimator_config_": self.estimator_config_
		}

	def __str__(self):
		return str(self.asdict())

