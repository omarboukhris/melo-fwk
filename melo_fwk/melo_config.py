
from mql import quantflow_factory
from melo_fwk.policies.vol_target_policy import VolTarget

import yaml
import glob

from pathlib import Path

from dataclasses import dataclass, field

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
	def strip(parsed_dict: dict, key: str):
		assert key in parsed_dict.keys(), f"Key [{key}] not in Dictionary keys [{parsed_dict.keys()}]"
		assert len(parsed_dict[key]) >= 1, f"Key [{key}] not in Dictionary keys [{parsed_dict.keys()}]"
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
	def build_estimator(quant_query_dict: dict):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "ProcessDef")
		estimator_kw = ConfigBuilderHelper.strip_single(stripped_entry, "Estimator")
		estimator_param_list = ConfigBuilderHelper.strip_single(stripped_entry, "EstimatorParamList").split(",")
		estimator_param_list = [estimator_param.strip() for estimator_param in estimator_param_list]
		
		_EstimatorObj = quantflow_factory.QuantFlowFactory.get_workflow(estimator_kw)
		return _EstimatorObj, estimator_param_list
		
class SizePolicyConfigBuilder:
	@staticmethod
	def build_size_policy(quant_query_dict: dict):
		position_size_dict = ConfigBuilderHelper.strip_single(quant_query_dict, "PositionSizing")

		size_policy_factory_name = ConfigBuilderHelper.strip_single(position_size_dict, "SizePolicy")
		assert size_policy_factory_name in quantflow_factory.QuantFlowFactory.size_policies.keys(), \
			f"{size_policy_factory_name} key is not in [{quantflow_factory.QuantFlowFactory.size_policies.keys()}]"
		_SizePolicyClass = quantflow_factory.QuantFlowFactory.get_size_policy(size_policy_factory_name)

		vol_target_cfg = ConfigBuilderHelper.parse_num_list(position_size_dict, "VolTargetCouple")
		vol_target = VolTarget(*vol_target_cfg)
		return _SizePolicyClass  # (vol_target)

class StrategyConfigBuilder:
	@staticmethod
	def build_strategy(quant_query_dict: dict, strat_config_registry: StratConfigRegistry):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "StrategiesDef")
		strategies_kw = ConfigBuilderHelper.strip_single(stripped_entry, "StrategyList").split(",")
		strat_config_points = ConfigBuilderHelper.strip_single(stripped_entry, "StrategyConfigList").split(",")

		strategies = []
		for strat, config in zip(strategies_kw, strat_config_points):
			# branch in case config is search space not config point
			strategies.append(
				quantflow_factory.QuantFlowFactory.get_strategy(strat.strip())(
					**strat_config_registry.get_strat_config(config.strip())
				)
			)

		forecast_weights_str = ConfigBuilderHelper.strip_single(stripped_entry, "forecastWeightsList")
		forecast_weights = [float(fw_str) for fw_str in forecast_weights_str.split(",")]

		return strategies, forecast_weights

class ProductConfigBuilder:
	@staticmethod
	def build_products(quant_query_dict: dict):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "ProductsDef")
		products_generator = ConfigBuilderHelper.strip_single(stripped_entry, "ProductsDefList")["ProductsGenerator"]
		instruments = stripped_entry["instrument"]  # if idx build index otherwise trade singles
		time_period = [int(year) for year in stripped_entry["timeperiod"]]

		output_products = {}
		for prods in products_generator:
			products_type = ConfigBuilderHelper.strip_single(prods, "productType")
			products_name_list = ConfigBuilderHelper.parse_list(prods, "ProductsList")
			for product_name in products_name_list:
				output_products.update(ProductConfigBuilder._get_product(products_type, product_name))

		if instruments == "idx":
			# build index
			pass
		# else: trade singles
		return output_products, time_period

	@staticmethod
	def _get_product(products_type: str, product_name: str) -> dict:
		product_factory_name = f"{products_type}.{product_name}"
		assert product_factory_name in quantflow_factory.QuantFlowFactory.products.keys(), \
			f"QuantFlowFactory: {product_factory_name} product key not in [{quantflow_factory.QuantFlowFactory.products.keys()}]"
		return {product_factory_name: quantflow_factory.QuantFlowFactory.get_product(product_factory_name)}

