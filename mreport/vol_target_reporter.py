import pandas as pd
from matplotlib import pyplot as plt

from mql.mconfig.melo_config import MeloConfig
from mreport.base_reporter import BaseReporter
from mreport.md_formatter import MdFormatter

class VolTargetReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		super(VolTargetReporter, self).__init__(input_config)

	def process_results(self, query_path: str, export_dir: str, raw_results: dict):
		export_dir = query_path + export_dir
		output_list = list(raw_results.values())
		result = pd.DataFrame(output_list[0])

		self.logger.info("Exporting Vol targetting results")
		ss = MdFormatter.h2("Volatility Target Results")
		png_filename = "assets/vol_target_report.png"
		ss += MdFormatter.image("Volatility Targeting Results", png_filename, "voltargetresults")

		for x in output_list[1:]:
			result["gar"] += x["gar"]
		result["gar"] = result["gar"] / len(output_list)

		# result.plot(x="vol_target", y="gar")
		result.ewm(span=3, adjust=False).mean().plot(x="vol_target", y="gar")
		plt.title("smoothed GAR = Ewm_3[f(VT)]")
		plt.savefig(f"{export_dir}/{png_filename}")
		plt.close()

		return ss
