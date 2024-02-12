import json

from mepo import estim
from mestimators.base_estimator import MeloBaseEstimator

from mutils.quantfactory_registry import QuantFlowRegistry

from mql.mql_parser import MqlParser

from pathlib import Path

from mutils.quantflow_factory import QuantFlowFactory


class MeloMachina:

	@staticmethod
	def build_estimator(process, mql_config, config) -> MeloBaseEstimator:
		estimator_obj = QuantFlowFactory.get_estimator(process)
		with open(str(estim.estim_map.get(config)), "r") as fs:
			estim_config = json.load(fs)
		return estimator_obj(
			products=mql_config.products_config[0],
			time_period=mql_config.products_config[1],
			strategies=mql_config.strategies_config[0],
			forecast_weights=mql_config.strategies_config[1],
			size_policy=mql_config.size_policy,
			estimator_params=estim_config
		)

	def __init__(self):
		# register melo components in factory
		# registration comes after config loading
		# otherwise product factory would not be initialized
		QuantFlowRegistry.register_all()
		# setup mql parsers
		self.mql_parser = MqlParser()

	def run(self, book_path: Path, process: str, config: str, export_path: str):
		"""
		Estimators should:
			- Implement the same constructor (see any estimator)
			- Implement a run() method that returns any result
		"""
		mql_config = self.mql_parser.parse_to_config(str(book_path))
		estimator = MeloMachina.build_estimator(process, mql_config, config)
		output = estimator.run()

		# TODO: Broken here
		conf_dir = config.replace(".", "_")
		book_dir = str(book_path.name).replace(".", "_")
		process_dir = process.replace(".", "_")
		export_path = Path(export_path) / f"{book_dir}/{process_dir}/{conf_dir}/"
		export_path.mkdir(parents=True, exist_ok=True)
		mql_config.write_report(process, output, str(export_path))

