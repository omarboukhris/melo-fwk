
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.config.config_helper import ConfigBuilderHelper


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

		_EstimatorObj = QuantFlowFactory.get_estimator(estimator_kw)
		return _EstimatorObj, estimator_param_list

