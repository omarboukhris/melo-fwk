import pandas as pd
import tqdm

from melo_fwk.config.melo_config import MeloConfig
from melo_fwk.reporters.base_reporter import BaseReporter
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.loggers.global_logger import GlobalLogger

class ForecastWeightsReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		self.logger = GlobalLogger.build_composite_for("ForecastWeightsReporter")
		self.logger.info("Initializing ForecastWeightsReporter")
		super(ForecastWeightsReporter, self).__init__(input_config)

	def header(self):
		self.logger.info("Writing header")
		return self.std_header()

	def process_results(self, query_path: str, export_dir: str, raw_results: dict):
		export_dir = query_path + export_dir
		self.logger.info("Exporting optimizarion results")
		ss = MdFormatter.h2("Optimization Results")
		for product_name, opt_df in tqdm.tqdm(raw_results.items(), leave=False):

			assert isinstance(opt_df, pd.DataFrame), \
				f"(ForecastWeightsReporter) TSAR result {product_name} is not associated to a pandas DataFrame"

			ss += MdFormatter.bold(f"For product {MdFormatter.italic(product_name)}") + "\n"
			opt_items = []
			# for idx, opt in opt_df.iterrows():
			# 	sr = opt["OptimResult.fun"]
			# 	fw = opt["OptimResult.x"]
			# 	div_mult = opt["DivMult"]
			#
			# 	opt_items.append(f"Year {idx}: forecast weight are {fw} with multiplier {div_mult} producing SR of {sr}")
			mean_sr = opt_df["OptimResult.fun"].mean()
			mean_fw = opt_df["OptimResult.x"].mean()
			mean_div_mult = opt_df["DivMult"].mean()
			opt_items.append(f"forecast weight are {mean_fw} with multiplier {mean_div_mult} producing SR of {mean_sr}")
			ss += MdFormatter.item_list(opt_items) + "\n"

		return ss
