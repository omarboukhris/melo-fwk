import pandas as pd
import tqdm

from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.market_data.compo_market_loader import CompositeMarketLoader
from melo_fwk.strategies import BuyAndHold
from melo_fwk.utils.generic_config_loader import GenericConfigLoader
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.config.mql_dict import MqlDict
from melo_fwk.utils import yaml_io
from dataclasses import dataclass, asdict
from pathlib import Path

import glob

from melo_fwk.utils.weights import Weights


@dataclass(frozen=True)
class StratConfigRegistry:
	config_points_registry: dict

	def __str__(self):
		return str(self.config_points_registry)

	@staticmethod
	def export_strat_config_node(opt, export_path: str, strat_name: str) -> None:
		strat_config_df = pd.DataFrame({
			"score_vals": -opt.optimizer_results_[0].func_vals,
			"x_iters": opt.optimizer_results_[0].x_iters
		}).sort_values(by=["score_vals"], ascending=False).drop_duplicates(subset=["score_vals"])
		# might eliminate different candidates with exact same score (low probability but exists)

		config_list = {}
		market = CompositeMarketLoader.from_config(GenericConfigLoader.get_node(CompositeMarketLoader.__name__, {}))
		strat_class_ = QuantFlowFactory.get_strategy(strat_name)
		for i, (_, config_pt) in tqdm.tqdm(enumerate(strat_config_df.head(5).iterrows()), leave=False):
			# remove (product, strat_class, size_policy, metric)
			params = [p for p in config_pt["x_iters"] if type(p) in [int, float]]
			strat = asdict(strat_class_(*params).estimate_forecast_scale(market))
			strat.pop("search_space", None)
			config_list[f"{strat_name}_{i}"] = strat

		yaml_io.write_strat_config_point(config_list, export_path + f"/{strat_name}.yml")

	def get_strat_config(self, key: str) -> dict:
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
	def build_registry(strat_config_points: str):
		"""
		Register config points for current mql query
		"""
		config_points_filenames = glob.glob(f"{strat_config_points}/*")

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
	def build_strategy(mql_dict: MqlDict, strat_config_registry: StratConfigRegistry):
		logger = GlobalLogger.build_composite_for("StratConfigBuilder")
		if "StrategiesDef" not in mql_dict.keys():
			logger.warn("No Strategies Parsed; Using default BuyAndHold")
			return [BuyAndHold()], Weights([1.], 1.)

		strat_mql_dict = mql_dict.strip_single("StrategiesDef")
		strategies_kw = strat_mql_dict.strip_single("AlphanumList").split(",")
		strat_config_points = strat_mql_dict.parse_list("StrategyConfigList")

		logger.info(f"Loading Strategies {[s.strip() for s in strategies_kw]}")
		strategies = []
		for strat, config in zip(strategies_kw, strat_config_points):
			if "." in config:
				# look for key in search space registry
				# only used when running strat optim
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

		if "WeightsList" not in strat_mql_dict.keys():
			logger.warn("No ForecastWeights Parsed; Using default 1/n")
			return strategies, Weights([1/len(strategies) for _ in strategies], 1.)

		forecast_weights = strat_mql_dict.parse_num_list("WeightsList")

		if "DivMult" not in strat_mql_dict.keys():
			logger.warn("No DivMult Parsed; Using default 1.")
			return strategies, Weights(forecast_weights, 1.)

		divmult = float(strat_mql_dict.strip_single("DivMult"))

		logger.info(f"DivMult Parsed; Using {divmult}")
		return strategies, Weights(forecast_weights, divmult)


