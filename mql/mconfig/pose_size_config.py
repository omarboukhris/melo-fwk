from dataclasses import dataclass

from melo_fwk.pose_size import BaseSizePolicy
from melo_fwk.quantflow_factory import QuantFlowFactory
from mql.mconfig.mql_dict import MqlDict
from melo_fwk.loggers.global_logger import GlobalLogger


@dataclass
class SizePolicyConfigBuilder:

	@staticmethod
	def get_vol_target_params(mql_dict: MqlDict):
		logger = GlobalLogger.build_composite_for("VolTargetConfigBuilder")
		if "PositionSizing" not in mql_dict.keys():
			logger.warn("No VolTarget parsed; Using default (0, 0).")
			# annual_vol_target, trading_capital
			return 0., 0.

		position_size_mql_dict = mql_dict.get_node("PositionSizing")
		if "VolTargetCouple" in position_size_mql_dict.keys():
			vol_target_cfg = position_size_mql_dict.parse_num_list("VolTargetCouple")
			logger.info(f"Parsed VolTarget from Query {vol_target_cfg}")
			return vol_target_cfg
		logger.warn("No VolTarget parsed; Using default (0, 0).")
		# annual_vol_target, trading_capital
		return 0., 0.

	@staticmethod
	def build_size_policy(mql_dict: MqlDict) -> BaseSizePolicy:
		vol_target_params = SizePolicyConfigBuilder.get_vol_target_params(mql_dict)

		logger = GlobalLogger.build_composite_for("SizePolicyConfigBuilder")
		if "PositionSizing" not in mql_dict.keys():
			logger.warn("No PositionSizing Parsed; Using default BaseSizePolicy")
			return QuantFlowFactory.get_size_policy("default")(*vol_target_params)

		position_size_mql_dict = mql_dict.get_node("PositionSizing")

		size_policy_factory_name = position_size_mql_dict.get_node("SizePolicy")
		assert size_policy_factory_name in QuantFlowFactory.size_policies.keys(), logger.error(
			f"{size_policy_factory_name} key is not in [{QuantFlowFactory.size_policies.keys()}]")
		logger.info(f"PositionSizing Parsed; using {size_policy_factory_name}")
		return QuantFlowFactory.get_size_policy(size_policy_factory_name)(*vol_target_params)

