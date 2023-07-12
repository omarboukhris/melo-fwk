from dataclasses import dataclass

from melo_fwk.pose_size import BaseSizePolicy
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.config.config_helper import ConfigBuilderHelper
from melo_fwk.loggers.global_logger import GlobalLogger


@dataclass
class SizePolicyConfigBuilder:

	@staticmethod
	def get_vol_target_params(quant_query_dict: dict):
		logger = GlobalLogger.build_composite_for("VolTargetConfigBuilder")
		if "PositionSizing" not in quant_query_dict.keys():
			logger.warn("No VolTarget parsed; Using default (0, 0).")
			# annual_vol_target, trading_capital
			return 0., 0.

		position_size_dict = ConfigBuilderHelper.strip_single(quant_query_dict, "PositionSizing")
		if "VolTargetCouple" in position_size_dict.keys():
			vol_target_cfg = ConfigBuilderHelper.parse_num_list(position_size_dict, "VolTargetCouple")
			logger.info(f"Parsed VolTarget from Query {vol_target_cfg}")
			return vol_target_cfg
		logger.warn("No VolTarget parsed; Using default (0, 0).")
		# annual_vol_target, trading_capital
		return 0., 0.

	@staticmethod
	def build_size_policy(quant_query_dict: dict) -> BaseSizePolicy:
		vol_target_params = SizePolicyConfigBuilder.get_vol_target_params(quant_query_dict)

		logger = GlobalLogger.build_composite_for("SizePolicyConfigBuilder")
		if "PositionSizing" not in quant_query_dict.keys():
			logger.warn("No PositionSizing Parsed; Using default BaseSizePolicy")
			return QuantFlowFactory.get_size_policy("default")(*vol_target_params)

		position_size_dict = ConfigBuilderHelper.strip_single(quant_query_dict, "PositionSizing")

		size_policy_factory_name = ConfigBuilderHelper.strip_single(position_size_dict, "SizePolicy")
		assert size_policy_factory_name in QuantFlowFactory.size_policies.keys(), logger.error(
			f"{size_policy_factory_name} key is not in [{QuantFlowFactory.size_policies.keys()}]")
		logger.info(f"PositionSizing Parsed; using {size_policy_factory_name}")
		return QuantFlowFactory.get_size_policy(size_policy_factory_name)(*vol_target_params)

