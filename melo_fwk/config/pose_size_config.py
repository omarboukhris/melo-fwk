
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.size_policies.vol_target import VolTarget
from melo_fwk.config.config_helper import ConfigBuilderHelper
from melo_fwk.loggers.global_logger import GlobalLogger

class VolTargetConfigBuilder:
	@staticmethod
	def build_vol_target(quant_query_dict: dict):
		logger = GlobalLogger.build_composite_for("VolTargetConfigBuilder")
		if not ConfigBuilderHelper.is_key_present(quant_query_dict, "PositionSizing"):
			logger.warn("No VolTarget parsed; Using default (0, 0).")
			return VolTarget(annual_vol_target=0., trading_capital=0.)

		position_size_dict = ConfigBuilderHelper.strip_single(quant_query_dict, "PositionSizing")
		if "VolTargetCouple" in position_size_dict.keys():
			vol_target_cfg = ConfigBuilderHelper.parse_num_list(position_size_dict, "VolTargetCouple")
			logger.info(f"Parsed VolTarget from Query {vol_target_cfg}")
			return VolTarget(*vol_target_cfg)
		logger.warn("No VolTarget parsed; Couldn't parse VolTarget couple")
		return None

class SizePolicyConfigBuilder:
	@staticmethod
	def build_size_policy(quant_query_dict: dict):
		logger = GlobalLogger.build_composite_for("SizePolicyConfigBuilder")
		if not ConfigBuilderHelper.is_key_present(quant_query_dict, "PositionSizing"):
			logger.warn("No PositionSizing Parsed; Using default BuyAndHold")
			return QuantFlowFactory.get_size_policy("default")

		position_size_dict = ConfigBuilderHelper.strip_single(quant_query_dict, "PositionSizing")

		size_policy_factory_name = ConfigBuilderHelper.strip_single(position_size_dict, "SizePolicy")
		assert size_policy_factory_name in QuantFlowFactory.size_policies.keys(), logger.error(
			f"{size_policy_factory_name} key is not in [{QuantFlowFactory.size_policies.keys()}]")
		logger.info(f"PositionSizing Parsed; using {size_policy_factory_name}")
		return QuantFlowFactory.get_size_policy(size_policy_factory_name)
