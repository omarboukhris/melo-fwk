from typing import Tuple, Dict

import pandas as pd
import tqdm

from melo_fwk.basket.var_basket import VaRBasket
from melo_fwk.config.melo_config import MeloConfig
from melo_fwk.reporters.base_reporter import BaseReporter
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.plots.var_plot import VarPlotter
from melo_fwk.loggers.global_logger import GlobalLogger

class VaRReporter(BaseReporter):

	def __init__(self, input_config: MeloConfig):
		self.logger = GlobalLogger.build_composite_for("BacktestReporter")
		self.logger.info("Initializing BacktestReporter")
		super(VaRReporter, self).__init__(input_config)

	def process_results(
		self, query_path: str, export_dir: str,
		raw_results: Tuple[pd.DataFrame, Dict[int, VaRBasket], Tuple]):
		"""
		raw_results dict :
			key = product name
			Value = dict :
				key = product_filepath + year
				value = TSAR
		"""
		out_dict, var_basket_map, var_config = raw_results
		method, var_params = var_config
		export_dir = query_path + export_dir + "/assets/"
		self.logger.info("Exporting VaR Results")

		ss = MdFormatter.h2("VaR Estimation Results")
		ss += f"\n{out_dict.to_markdown()}\n"

		for year, var_basket in tqdm.tqdm(var_basket_map.items(), leave=False):
			if method == "mc":
				prices = var_basket.simulate_price(*var_params)
				price_paths = var_basket.simulate_price_paths(*var_params)
			else:
				prices = var_basket.simulate_hist(*var_params)
				price_paths = var_basket.simulate_hist_paths(*var_params)

			ss += MdFormatter.h2(f"Year {year}\n")

			export_list = [
				f"{export_dir}/{p.name}_{year}.png"
				for p in var_basket.products
			]
			export_path_list = [
				f"{export_dir}/{p.name}_path_{year}.png"
				for p in var_basket.products
			]

			for p, path, product in zip(export_list, export_path_list, var_basket.products):

				ss += MdFormatter.h3(product.name)
				ss += MdFormatter.image(
					f"price histogram after year {year}",
					p, f"price_histogram_after_year_{year}",
				)

				ss += MdFormatter.image(
					f"price path, year {year}",
					path, f"price_path_year_{year}",
				)

			VarPlotter.save_prices(
				prices, export_filename=export_list)

			VarPlotter.save_price_paths(
				price_paths, var_basket.tails,
				export_filename=export_path_list)

		# VarPlotter.plot_prices(basket.simulate_hist(n_days, r_spl))
		# VarPlotter.plot_prices(basket.simulate_price(n_days, n_sim))
		# VarPlotter.plot_price_paths(basket.simulate_price_paths(n_days, n_sim), basket.tails)
		# VarPlotter.plot_price_paths(basket.simulate_hist_paths(n_days, r_spl), basket.tails)

		return ss
