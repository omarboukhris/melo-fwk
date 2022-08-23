
from rules import ewma_rule, sma_rule
from datastreams import backtest_data_loader as btdl
from helpers.plots import ForecastPlotter

import pandas as pd
import tqdm

from typing import List

import unittest

class TestRulesHelper:

	ewma_meta_default = {
		"fast": 2,
		"slow": 8,
		"multiplier": 1.9,
		"iterations": 6,
		"scale": 20,
		"cap": 20
	}

	sma_meta_default = {
		"fast": 2,
		"slow": 8,
		"multiplier": 1.9,
		"iterations": 6,
		"scale": 20,
		"cap": 20
	}

	@staticmethod
	def test_moving_average_with_residue(
		product_list: List[dict],
		metaparams: dict,
		rule_name: str,
		RuleClass: callable,
		DataLoader_fn: callable):

		for product in tqdm.tqdm(product_list):
			params = {
				"fast_span": metaparams["fast"],
				"slow_span": metaparams["slow"],
				"scale": metaparams["scale"],
				"cap": metaparams["cap"],
			}

			for _ in tqdm.tqdm(range(metaparams["iterations"])):
				ewma_tr = RuleClass(**params)
				input_df, pds = DataLoader_fn(product)
				simulation_result_df = pd.DataFrame(TestRulesHelper.run_simulation(ewma_tr, pds))
				plotter = ForecastPlotter(simulation_result_df, input_df)
				plotter.plot_twinx()
				plotter.save_png(f"data/residual/{rule_name}_{product['name']}_{int(params['fast_span'])}_{int(params['slow_span'])}.png")

				params["fast_span"] = params["fast_span"] * metaparams["multiplier"]
				params["slow_span"] = params["slow_span"] * metaparams["multiplier"]

	@staticmethod
	def test_ewma_with_residue(product_list: List[dict], ewma_metaparams: dict):
		TestRulesHelper.test_moving_average_with_residue(
			product_list,
			ewma_metaparams,
			"ewma",
			ewma_rule.EWMATradingRule,
			btdl.BacktestDataLoader.get_product_datastream)

	@staticmethod
	def test_sma_with_residue(product_list: List[dict], sma_metaparams: dict):
		TestRulesHelper.test_moving_average_with_residue(
			product_list,
			sma_metaparams,
			"sma",
			sma_rule.SMATradingRule,
			btdl.BacktestDataLoader.get_product_datastream)

	@staticmethod
	def test_mock_ewma_with_residue(product_list: List[dict], ewma_metaparams: dict):
		TestRulesHelper.test_moving_average_with_residue(
			product_list,
			ewma_metaparams,
			"ewma",
			ewma_rule.EWMATradingRule,
			btdl.BacktestDataLoader.get_mock_datastream)

	@staticmethod
	def test_mock_sma_with_residue(product_list: List[dict], sma_metaparams: dict):
		TestRulesHelper.test_moving_average_with_residue(
			product_list,
			sma_metaparams,
			"sma",
			sma_rule.SMATradingRule,
			btdl.BacktestDataLoader.get_mock_datastream)

	@staticmethod
	def run_simulation(ewma_tr, pds):
		output_forcast = []
		for _ in pds:
			window = pds.get_window()
			if window is not None:
				output_forcast.append({
					"Date": pds.get_current_date(),
					"Forecast": ewma_tr.forecast(window),
				})
		return output_forcast

class RulesUnitTest(unittest.TestCase):
	def test_ewma(self):
		products = btdl.BacktestDataLoader.get_products("data/Stocks/*1d_10y.csv")
		ewma_meta = TestRulesHelper.ewma_meta_default
		TestRulesHelper.test_ewma_with_residue(
			products,
			ewma_meta
		)


	def test_sma(self):
		products = btdl.BacktestDataLoader.get_products("data/Stocks/*1d_10y.csv")
		sma_meta = TestRulesHelper.ewma_meta_default
		TestRulesHelper.test_sma_with_residue(
			products,
			sma_meta,
		)


	def test_mock_ewma(self):
		ewma_meta = TestRulesHelper.ewma_meta_default
		TestRulesHelper.test_mock_ewma_with_residue(
			[{"name": "mock"}],
			ewma_meta
		)


	def test_mock_sma(self):
		sma_meta = TestRulesHelper.ewma_meta_default
		TestRulesHelper.test_mock_sma_with_residue(
			[{"name": "mock"}],
			sma_meta,
		)


if __name__ == "__main__":
	unittest.main()
