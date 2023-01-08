import os
from dataclasses import dataclass

from melo_fwk.reporters.md_formatter import MdFormatter


@dataclass(frozen=True)
class CommonMeloConfig:
	name: str
	reporter_class_: callable  # Type[BaseReporter]

	def __check_export_directories(self, output_dir):
		if not os.path.isdir(output_dir):
			os.mkdir(output_dir)
		if not os.path.isdir(output_dir + "/data/"):
			os.mkdir(output_dir + "/data/")
		if not os.path.isdir(output_dir + "/data/" + self.name):
			os.mkdir(output_dir + "/data/" + self.name)
		if not os.path.isdir(output_dir + "/data/" + self.name + "/assets/"):
			os.mkdir(output_dir + "/data/" + self.name + "/assets/")

	def write_report(self, estimator_results: dict, output_dir: str = "./"):
		"""
		NOTE: Generates artifacts (
			export folder: $query_name/report.md
			assets folder: $query_name/assets/*.png
		)
		:param estimator_results:
		:param output_dir:
		:return:
		"""
		reporter = self.reporter_class_(self)
		md_ss = reporter.header()
		self.__check_export_directories(output_dir)
		md_ss += reporter.process_results(output_dir, "/data/" + self.name, estimator_results)
		MdFormatter.save_md(output_dir + "/data/" + self.name, "report.md", md_ss)

