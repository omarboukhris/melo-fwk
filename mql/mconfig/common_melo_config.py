import os
from dataclasses import dataclass

from mreport.md_formatter import MdFormatter
from mutils.quantflow_factory import QuantFlowFactory


@dataclass(frozen=True)
class CommonMeloConfig:
	name: str
	# reporter_class_: callable  # Type[BaseReporter]

	def __check_export_directories(self, output_dir):
		if not os.path.isdir(output_dir):
			os.mkdir(output_dir)
		if not os.path.isdir(f"{output_dir}/{self.name}"):
			os.mkdir(f"{output_dir}/{self.name}")
		if not os.path.isdir(f"{output_dir}/{self.name}/assets/"):
			os.mkdir(f"{output_dir}/{self.name}/assets/")

	def write_report(self, estimator: str, estimator_results: dict, output_dir: str = "./"):
		"""
		NOTE: Generates artifacts (
			export folder: $query_name/report.md
			assets folder: $query_name/assets/*.png
		)
		:param estimator:
		:param estimator_results:
		:param output_dir:
		:return:
		"""
		reporter = QuantFlowFactory.get_reporter(estimator)(self)
		md_ss = reporter.header()
		self.__check_export_directories(output_dir)
		md_ss += reporter.process_results(output_dir, self.name, estimator_results)
		MdFormatter.save_md(f"{output_dir}/{self.name}", "report.md", md_ss)

