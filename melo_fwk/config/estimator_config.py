
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.config.config_helper import ConfigBuilderHelper


class EstimatorConfigBuilder:
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
	def get_estimator_params(quant_query_dict: dict):
		stripped_entry = ConfigBuilderHelper.strip_single(quant_query_dict, "ProcessDef")
		if ConfigBuilderHelper.is_key_present(stripped_entry, "EstimatorParamList"):
			estimator_param_list = ConfigBuilderHelper.strip_single(stripped_entry, "EstimatorParamList").split(",")
			estimator_param_list = [estimator_param.strip() for estimator_param in estimator_param_list]
			return estimator_param_list
		return []

	@staticmethod
	def build_estimator(quant_query_dict: dict):
		estimator_kw = EstimatorConfigBuilder.get_estimator_name(quant_query_dict)

		estimator_param_list = EstimatorConfigBuilder.get_estimator_params(quant_query_dict)

		_EstimatorObj = QuantFlowFactory.get_estimator(estimator_kw)
		return _EstimatorObj, estimator_param_list

