
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.config.config_helper import ConfigBuilderHelper

from dataclasses import dataclass, field
from pathlib import Path

import yaml
import glob


@dataclass(frozen=False)
class StratConfigRegistry:
	mql_query_path: str
	config_points_registry: dict = field(init=False)

	def __post_init__(self):
		"""
		Register config points for current mql query
		"""
		config_points_filenames = glob.glob(str(
			Path(self.mql_query_path) / "strat_config_points") + "/*")

		self.config_points_registry = {}
		for config_point_fn in config_points_filenames:
			with open(config_point_fn, "r") as stream:
				try:
					for strat_config in yaml.safe_load(stream):
						self.config_points_registry = dict(
							self.config_points_registry,
							**strat_config)
				except yaml.YAMLError as exc:
					print(exc)

	@staticmethod
	def sanitize_key(key: str):
		return ".".join([elm.strip() for elm in key.split(".")])

	def get_strat_config(self, key: str):
		"""
		:param key: Strat config or Strat search space registry key
		:return: Strat config or Strat search space
		"""
		if "." in key:
			return QuantFlowFactory.get_search_space(
				StratConfigRegistry.sanitize_key(key))
		else:
			return self.config_points_registry[key]

	def __str__(self):
		return str(self.config_points_registry)


class StrategyConfigBuilder:
	@staticmethod
	def build_strategy(quant_query_dict: dict, strat_config_registry: StratConfigRegistry):
		if not ConfigBuilderHelper.is_key_present(quant_query_dict, "StrategiesDef"):
			return [], []

		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "StrategiesDef")
		strategies_kw = ConfigBuilderHelper.strip_single(stripped_entry, "StrategyList").split(",")
		strat_config_points = ConfigBuilderHelper.strip_single(stripped_entry, "StrategyConfigList").split(",")

		strategies = []
		for strat, config in zip(strategies_kw, strat_config_points):
			if "." in config:
				# look for key in search space registry
				sanitized_config = StratConfigRegistry.sanitize_key(config)
				strategies.append((
					QuantFlowFactory.get_strategy(strat.strip()),
					strat_config_registry.get_strat_config(sanitized_config)
				))
			else:
				# look for key in strat config point registry
				strategies.append(
					QuantFlowFactory.get_strategy(strat.strip())(
						**strat_config_registry.get_strat_config(config.strip())
					)
				)

		if not ConfigBuilderHelper.is_key_present(stripped_entry, "forecastWeightsList"):
			return strategies, None

		forecast_weights_str = ConfigBuilderHelper.strip_single(stripped_entry, "forecastWeightsList")
		forecast_weights = [float(fw_str) for fw_str in forecast_weights_str.split(",")]

		return strategies, forecast_weights


