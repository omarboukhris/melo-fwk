
import unittest

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tqdm

from melo_fwk.market_data import CommodityDataLoader, FxDataLoader
from melo_fwk.trading_systems import TradingSystem, TradingSystemIter
from melo_fwk.strategies import EWMAStrategy
from melo_fwk.policies.size import VolTargetInertiaPolicy
from melo_fwk.plots import TsarPlotter

from melo_fwk.policies.var.var_policy import (
	ParametricVar,
	HistVar,
	MonteCarloVar
)

class VaRUnitTests(unittest.TestCase):

	def test_var(self):
		product = CommodityDataLoader.Gold
		# product = FxDataLoader.EURUSD

		strat = [
			EWMAStrategy(
				fast_span=16,
				slow_span=64,
				scale=16.,
			),
			EWMAStrategy(
				fast_span=8,
				slow_span=32,
			).estimate_forecast_scale()
		]
		fw = [0.4, 0.6]

		start_capital = 60000
		size_policy = VolTargetInertiaPolicy(
			annual_vol_target=25e-2,
			trading_capital=start_capital)

		trading_subsys = TradingSystem(
			product=product,
			trading_rules=strat,
			forecast_weights=fw,
			size_policy=size_policy
		)

		tsar = trading_subsys.run()

		years = [year for year in range(2004, 2008)]
		prod_datastream = product.get_years(years).datastream
		indexer = pd.api.indexers.FixedForwardWindowIndexer(window_size=250)
		rolling_datastream = prod_datastream.dataframe.rolling(window=indexer, step=20)
		for i, subset_prod_ds in tqdm.tqdm(enumerate(rolling_datastream), leave=False):
			print(subset_prod_ds)


		# pVaR_99p_10d = ParametricVar(alpha=0.01, n_days=1)
		# hist_VaR = HistVar(alpha=0.01, n_days=1)
		# var_list = []
		# for account in tqdm.tqdm(tsar.account_series.rolling(window=250, step=25, min_periods=250)):
		# 	if len(account) <= 1:
		# 		continue
		# 	account -= account.iat[0]  # offset the account series
		# 	var_list.append(pVaR_99p_10d(start_capital+account))
		# 	# var_list.append(hist_VaR(start_capital+account))
		# print(len(var_list), var_list)
		#
		# plt.hist(var_list, bins=100)
		# plt.show()
		# plt.close()


if __name__ == "__main__":
	unittest.main()

