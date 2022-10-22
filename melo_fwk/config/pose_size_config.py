
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.position_size_policies.vol_target import VolTarget
from melo_fwk.config.config_helper import ConfigBuilderHelper


class VolTargetConfigBuilder:
	@staticmethod
	def build_vol_target(quant_query_dict: dict):
		if not ConfigBuilderHelper.is_key_present(quant_query_dict, "PositionSizing"):
			return VolTarget(annual_vol_target=0., trading_capital=0.)

		position_size_dict = ConfigBuilderHelper.strip_single(quant_query_dict, "PositionSizing")
		if "VolTargetCouple" in position_size_dict.keys():
			vol_target_cfg = ConfigBuilderHelper.parse_num_list(position_size_dict, "VolTargetCouple")
			return VolTarget(*vol_target_cfg)
		return None

class SizePolicyConfigBuilder:
	@staticmethod
	def build_size_policy(quant_query_dict: dict):
		if not ConfigBuilderHelper.is_key_present(quant_query_dict, "PositionSizing"):
			return QuantFlowFactory.get_size_policy("default")

		position_size_dict = ConfigBuilderHelper.strip_single(quant_query_dict, "PositionSizing")

		size_policy_factory_name = ConfigBuilderHelper.strip_single(position_size_dict, "SizePolicy")
		assert size_policy_factory_name in QuantFlowFactory.size_policies.keys(), \
			f"{size_policy_factory_name} key is not in [{QuantFlowFactory.size_policies.keys()}]"
		return QuantFlowFactory.get_size_policy(size_policy_factory_name)
