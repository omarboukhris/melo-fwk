
from rules import ewma_rule, sma_rule
from datastreams import datastream as ds
from helpers import AccountPlotter

import pandas as pd
import tqdm, glob
from typing import List

class TestRules:

	ewma_meta_default = {
		"fast": 2,
		"slow": 8,
		"multiplier": 1.5,
		"iterations": 6,
		"scale": 20,
		"cap": 20
	}

	sma_meta_default = {
		"fast": 2,
		"slow": 8,
		"multiplier": 1.5,
		"iterations": 6,
		"scale": 20,
		"cap": 20
	}

	@staticmethod
	def get_products(path: str):
		product_path_list = glob.glob(path)
		output = []
		for path in product_path_list:
			product_name = path.split("/")[-1][:-4]
			output.append({"name": product_name, "datasource": path})
		return output

	@staticmethod
	def test_moving_average_with_residue(product_list: List[dict], ewma_metaparams: dict, RuleClass: callable, rule_name: str):
		for product in tqdm.tqdm(product_list):
			ewma_params = {
				"fast_span": ewma_metaparams["fast"],
				"slow_span": ewma_metaparams["slow"],
				"scale": ewma_metaparams["scale"],
				"cap": ewma_metaparams["cap"],
			}
			for _ in tqdm.tqdm(range(ewma_metaparams["iterations"])):
				input_df = pd.read_csv(product["datasource"])
				pds = ds.PandasDataStream(product["name"], input_df)
				ewma_tr = RuleClass(rule_name, ewma_params)

				simulation_result_df = pd.DataFrame(TestRules.run_simulation(ewma_tr, pds))
				acc_plt = AccountPlotter(simulation_result_df, input_df)
				acc_plt.plot_twinx()
				acc_plt.save_png(f"data/residual/ewma_{product['name']}_{ewma_params['fast_span']}_{ewma_params['slow_span']}.png")

				ewma_params["fast_span"] = ewma_params["fast_span"] * ewma_metaparams["multiplier"]
				ewma_params["slow_span"] = ewma_params["slow_span"] * ewma_metaparams["multiplier"]

	@staticmethod
	def test_ewma_with_residue(product_list: List[dict], ewma_metaparams: dict):
		TestRules.test_moving_average_with_residue(product_list, ewma_metaparams, ewma_rule.EWMATradingRule, "ewma")

	@staticmethod
	def test_sma_with_residue(product_list: List[dict], ewma_metaparams: dict):
		TestRules.test_moving_average_with_residue(product_list, ewma_metaparams, sma_rule.SMATradingRule, "sma")

	@staticmethod
	def run_simulation(ewma_tr, pds):
		output_forcast = []
		for _ in pds:
			window = pds.get_window()
			if window is not None:
				output_forcast.append({
					"Date": pds.get_current_date(),
					"Balance": ewma_tr.forecast(window),
				})
		return output_forcast


if __name__ == "__main__":

	TestRules.test_ewma_with_residue(
		TestRules.get_products("data/Stocks/*.csv"),
		TestRules.ewma_meta_default,
	)

	TestRules.test_sma_with_residue(
		TestRules.get_products("data/Stocks/*.csv"),
		TestRules.sma_meta_default,
	)

