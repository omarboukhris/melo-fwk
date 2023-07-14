from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.utils.generic_config_loader import GenericConfigLoader
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.config.config_helper import ConfigBuilderHelper


class EstimatorConfigBuilder:

	@staticmethod
	def get_export_name(quant_query_dict: dict):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "ProcessDef")
		if "ExportName" in stripped_entry.keys():
			return ConfigBuilderHelper.strip_single(stripped_entry, "ExportName")
		else:
			return None

	@staticmethod
	def get_reporter(quant_query_dict: dict):
		estim_name = EstimatorConfigBuilder.get_estimator_name(quant_query_dict)
		return QuantFlowFactory.get_reporter(estim_name)

	@staticmethod
	def get_estimator_name(quant_query_dict: dict):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "ProcessDef")
		estimator_kw = ConfigBuilderHelper.strip_single(stripped_entry, "Estimator")
		return estimator_kw

	@staticmethod
	def build_estimator(quant_query_dict: dict):
		estimator_kw = EstimatorConfigBuilder.get_estimator_name(quant_query_dict)

		# estimator_param_list = EstimatorConfigBuilder.get_estimator_params(quant_query_dict)

		_EstimatorObj = QuantFlowFactory.get_estimator(estimator_kw)
		# return _EstimatorObj, estimator_param_list
		return _EstimatorObj, GenericConfigLoader.get_node(estimator_kw)

