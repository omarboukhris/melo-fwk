
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.policies.vol_target_policy import VolTarget
from melo_fwk.datastreams.index_builder import IndexBuilder

from dataclasses import dataclass, field
from pathlib import Path

import yaml
import glob

@dataclass(frozen=False)
class StratConfigRegistry:
	mql_query_path: str
	config_points_registry: dict = field(init=False)

	def __post_init__(self):
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

	def get_strat_config(self, key: str):
		return self.config_points_registry[key]

	def __str__(self):
		return str(self.config_points_registry)

class ConfigBuilderHelper:
	@staticmethod
	def is_key_present(parsed_dict: dict, key: str):
		return key in parsed_dict.keys()

	@staticmethod
	def strip(parsed_dict: dict, key: str):
		assert ConfigBuilderHelper.is_key_present(parsed_dict, key), \
			f"Key [{key}] not in Dictionary keys [{parsed_dict.keys()}]"
		assert len(parsed_dict[key]) >= 1, \
			f"Key [{key}] not in Dictionary keys [{parsed_dict.keys()}]"
		return parsed_dict[key]

	@staticmethod
	def strip_single(parsed_dict: dict, key: str):
		return ConfigBuilderHelper.strip(parsed_dict, key)[0]

	@staticmethod
	def parse_list(parsed_dict: dict, key: str):
		str_list = ConfigBuilderHelper.strip_single(parsed_dict, key)
		return [e.strip() for e in str_list.split(",")]

	@staticmethod
	def parse_num_list(parsed_dict: dict, key: str):
		str_list = ConfigBuilderHelper.strip_single(parsed_dict, key)
		return [float(e.strip()) for e in str_list.split(",")]

class EstimatorConfigBuilder:
	@staticmethod
	def get_estimator_name(quant_query_dict: dict):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "ProcessDef")
		estimator_kw = ConfigBuilderHelper.strip_single(stripped_entry, "Estimator")
		return estimator_kw

	@staticmethod
	def get_estimator_params(quant_query_dict: dict):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "ProcessDef")
		estimator_param_list = ConfigBuilderHelper.strip_single(stripped_entry, "EstimatorParamList").split(",")
		estimator_param_list = [estimator_param.strip() for estimator_param in estimator_param_list]
		return estimator_param_list

	@staticmethod
	def build_estimator(quant_query_dict: dict):
		estimator_kw = EstimatorConfigBuilder.get_estimator_name(quant_query_dict)
		estimator_param_list = []
		if ConfigBuilderHelper.is_key_present(quant_query_dict, "EstimatorParamList"):
			estimator_param_list = EstimatorConfigBuilder.get_estimator_params(quant_query_dict)

		_EstimatorObj = QuantFlowFactory.get_workflow(estimator_kw)
		return _EstimatorObj, estimator_param_list

class VolTargetConfigBuilder:
	@staticmethod
	def build_vol_target(quant_query_dict: dict):
		if not ConfigBuilderHelper.is_key_present(quant_query_dict, "PositionSizing"):
			return VolTarget(annual_vol_target=0., trading_capital=0.)

		position_size_dict = ConfigBuilderHelper.strip_single(quant_query_dict, "PositionSizing")
		vol_target_cfg = ConfigBuilderHelper.parse_num_list(position_size_dict, "VolTargetCouple")
		return VolTarget(*vol_target_cfg)

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
			# branch here in case config is search space not config point
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

class ProductConfigBuilder:
	@staticmethod
	def build_products(quant_query_dict: dict):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "ProductsDef")
		products_generator = ConfigBuilderHelper.strip_single(stripped_entry, "ProductsDefList")["ProductsGenerator"]
		instruments = ConfigBuilderHelper.strip_single(stripped_entry, "instrument")
		time_period = [int(year) for year in stripped_entry["timeperiod"]]

		output_products = {}
		for prods in products_generator:
			products_type = ConfigBuilderHelper.strip_single(prods, "productType")
			products_name_list = ConfigBuilderHelper.parse_list(prods, "ProductsList")
			for product_name in products_name_list:
				output_products.update(ProductConfigBuilder._get_product(products_type, product_name))

		# if idx build index otherwise trade singles
		if instruments == "idx":
			return IndexBuilder.build(output_products), time_period
		# else: trade singles
		return output_products, time_period

	@staticmethod
	def _get_product(products_type: str, product_name: str) -> dict:
		product_factory_name = f"{products_type}.{product_name}"
		assert product_factory_name in QuantFlowFactory.products.keys(), \
			f"QuantFlowFactory: {product_factory_name} product key not in [{QuantFlowFactory.products.keys()}]"
		return {product_factory_name: QuantFlowFactory.get_product(product_factory_name)}

