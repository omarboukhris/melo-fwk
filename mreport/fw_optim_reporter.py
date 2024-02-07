import pandas as pd
import tqdm

from mql.mconfig.melo_config import MeloConfig
from mreport.base_reporter import BaseReporter
from mreport.md_formatter import MdFormatter

class ForecastWeightsReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		super(ForecastWeightsReporter, self).__init__(input_config)

	def process_results(self, query_path: str, export_dir: str, raw_results: dict):
		self.logger.info("Exporting optimizarion results")
		ss = MdFormatter.h2("Optimization Results")
		for product_name, opt_df in tqdm.tqdm(raw_results.items(), leave=False):

			assert isinstance(opt_df, pd.DataFrame), \
				f"(ForecastWeightsReporter) TSAR result {product_name} is not associated to a pandas DataFrame"

			ss += MdFormatter.h3(f"For product {MdFormatter.italic(product_name)}") + "\n"
			mean_sr = opt_df["OptimResult.fun"].mean()
			mean_fw = opt_df["OptimResult.x"].mean()
			mean_div_mult = opt_df["DivMult"].mean()
			opt_items = f"forecast weight are {mean_fw} with multiplier {mean_div_mult} producing SR of {mean_sr}"
			ss += MdFormatter.item_list([opt_items]) + "\n"
			ss += opt_df.to_markdown() + "\n"

		return ss
