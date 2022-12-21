from melo_fwk.loggers.global_logger import GlobalLogger
from minimelo.strategies import BuyAndHold
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.config.config_helper import ConfigBuilderHelper
from melo_fwk.utils import yaml_io
from dataclasses import dataclass
from pathlib import Path

import glob


@dataclass(frozen=True)
class StratConfigRegistry:
	config_points_registry: dict

	def __str__(self):
		return str(self.config_points_registry)

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


	@staticmethod
	def build_registry(mql_query_path: str):
		"""
		Register config points for current mql query
		"""
		config_points_filenames = glob.glob(
			str(Path(mql_query_path) / "strat_config_points") + "/*")

		config_points_registry = {}
		for config_point_fn in config_points_filenames:
			config_points = yaml_io.read_strat_config_point(config_point_fn)
			config_points_registry.update(config_points)

		return StratConfigRegistry(config_points_registry=config_points_registry)


	@staticmethod
	def sanitize_key(key: str):
		return ".".join([elm.strip() for elm in key.split(".")])


class StrategyConfigBuilder:
	@staticmethod
	def build_strategy(quant_query_dict: dict, strat_config_registry: StratConfigRegistry):
		logger = GlobalLogger.build_composite_for("StratConfigBuilder")
		if "StrategiesDef" not in quant_query_dict.keys():
			logger.warn("No Strategies Parsed; Using default BuyAndHold")
			return [BuyAndHold()], [1.]

		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "StrategiesDef")
		strategies_kw = ConfigBuilderHelper.strip_single(stripped_entry, "StrategyList").split(",")
		strat_config_points = ConfigBuilderHelper.strip_single(stripped_entry, "StrategyConfigList").split(",")

		logger.info(f"Loading Strategies {[s.strip() for s in strategies_kw]}")
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

		if "forecastWeightsList" not in stripped_entry.keys():
			logger.warn("No ForecastWeights Parsed; Using default 1/n")
			return strategies, [1/len(strategies) for _ in strategies]

		forecast_weights_str = ConfigBuilderHelper.strip_single(stripped_entry, "forecastWeightsList")
		forecast_weights = [float(fw_str) for fw_str in forecast_weights_str.split(",")]

		logger.info(f"ForecastWeights Parsed; Using {forecast_weights}")
		return strategies, forecast_weights


