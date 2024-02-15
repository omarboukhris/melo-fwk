
from mepo import strat_lib
from mutils.loggers.global_logger import GlobalLogger
from melo_fwk.strategies import BuyAndHold
from mutils.quantflow_factory import QuantFlowFactory
from mql.mconfig.mql_dict import MqlDict

from melo_fwk.basket.weights import Weights


class StrategyConfigBuilder:
	@staticmethod
	def build_strategy(mql_dict: MqlDict):
		logger = GlobalLogger.build_composite_for("StratConfigBuilder")
		if "StrategiesDef" not in mql_dict.keys():
			logger.warn("No Strategies Parsed; Using default BuyAndHold")
			return [BuyAndHold()], Weights([1.], 1.)

		strat_mql_dict = mql_dict.get_node("StrategiesDef")

		logger.info(f"Loading Strategies {str}")
		strat_config_list = strat_mql_dict.parse_list("StrategyConfigList")
		if any(["$" in cpt for cpt in strat_config_list]):
			# search space instantiation
			template_list = [QuantFlowFactory.get_search_space(cfg_pt[1:]) for cfg_pt in strat_config_list]
			strategies = [(template, template.search_space) for template in template_list]
		else:
			strat_config_map = [strat_lib.js.get(cfg_pt).copy() for cfg_pt in strat_config_list]
			strat_templates = [QuantFlowFactory.get_strategy(strat.pop("strat")) for strat in strat_config_map]
			strategies = [template(**config) for template, config in zip(strat_templates, strat_config_map)]

		if "WeightsList" not in strat_mql_dict.keys():
			logger.warn("No ForecastWeights Parsed; Using default 1/n")
			return strategies, Weights([1/len(strategies) for _ in strategies], 1.)

		forecast_weights = strat_mql_dict.parse_num_list("WeightsList")

		if "DivMult" not in strat_mql_dict.keys():
			logger.warn("No DivMult Parsed; Using default 1.")
			return strategies, Weights(forecast_weights, 1.)

		divmult = float(strat_mql_dict.get_node("DivMult"))

		logger.info(f"DivMult Parsed; Using {divmult}")
		return strategies, Weights(forecast_weights, divmult)


