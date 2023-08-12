from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.utils.generic_config_loader import GenericConfigLoader
from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.config.mql_dict import MqlDict


class EstimatorConfigBuilder:

	@staticmethod
	def get_export_name(mql_dict: MqlDict):
		process_mql_dict = mql_dict.strip_single("ProcessDef")
		if "ExportName" in process_mql_dict.keys():
			return process_mql_dict.strip_single("ExportName")
		else:
			return None

	@staticmethod
	def get_reporter(mql_dict: MqlDict):
		estim_name = EstimatorConfigBuilder.get_estimator_name(mql_dict)
		return QuantFlowFactory.get_reporter(estim_name)

	@staticmethod
	def get_estimator_name(mql_dict: MqlDict):
		process_mql_dict = mql_dict.strip_single("ProcessDef")
		estimator_kw = process_mql_dict.strip_single("Estimator")
		return estimator_kw

	@staticmethod
	def build_estimator(mql_dict: MqlDict):
		estimator_kw = EstimatorConfigBuilder.get_estimator_name(mql_dict)

		# estimator_param_list = EstimatorConfigBuilder.get_estimator_params(quant_query_dict)

		_EstimatorObj = QuantFlowFactory.get_estimator(estimator_kw)
		# return _EstimatorObj, estimator_param_list
		return _EstimatorObj, GenericConfigLoader.get_node(estimator_kw)

