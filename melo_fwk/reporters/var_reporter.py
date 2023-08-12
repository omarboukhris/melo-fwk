from typing import Dict

import matplotlib.pyplot as plt
import pandas as pd
import tqdm

from mql.mconfig.melo_config import MeloConfig
from melo_fwk.reporters.base_reporter import BaseReporter
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.loggers.global_logger import GlobalLogger

class VaRReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		self.logger = GlobalLogger.build_composite_for("VaRReporter")
		self.logger.info("Initializing BacktestReporter")
		super(VaRReporter, self).__init__(input_config)

	def process_results(
		self, query_path: str, export_dir: str,
		raw_results: Dict[str, pd.DataFrame]):
		"""
		raw_results dict :
			key = product name
			Value = dict :
				key = product_filepath + year
				value = TSAR
		"""
		out_dict = raw_results
		export_dir = query_path + export_dir + "/assets/"
		self.logger.info("Exporting VaR Results")

		ss = MdFormatter.h2("VaR Estimation Results")
		# ss += f"\n{out_dict.to_markdown()}\n"

		for product_name, var_df in tqdm.tqdm(out_dict.items(), leave=False):
			ss += MdFormatter.h3(f"Product VaR {product_name} :\n")
			ss += f"\n{var_df.to_markdown(index='idx')}\n"

			export_filename = f"{export_dir}/{product_name}_hist.png"
			ss += MdFormatter.bold(MdFormatter.italic(f"VaR histograms for product {product_name}")) + "\n\n"

			ss += MdFormatter.image(
				f"price histogram for product {product_name}",
				export_filename,
				f"price histogram for product {product_name}",
			)

			var_df.hist(column=["var99", "cvar", "var99_rand_shock_20_5", "cvar_rand_shock_20_5"], bins=8)
			plt.savefig(export_filename)

		return ss
