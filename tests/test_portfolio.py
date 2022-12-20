from melo_fwk.loggers.console_logger import ConsoleLogger
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.trading_systems import TradingSystemIter

from melo_fwk.market_data import MarketDataLoader

from melo_fwk.strategies import EWMAStrategy
from melo_fwk.pose_size import VolTargetInertiaPolicy

from melo_fwk.plots import AccountPlotter, TsarPlotter

import pandas as pd
import tqdm
import unittest

class PortfolioUnitTests(unittest.TestCase):

	def init(self):
		GlobalLogger.set_loggers([ConsoleLogger])
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)

	def test_portfolio(self):
		self.init()
		sma_params = {
			"fast_span": 16,
			"slow_span": 64,
			"scale": 16,
		}
		sma = EWMAStrategy(**sma_params)

		products = MarketDataLoader.get_fx()
		products += MarketDataLoader.get_commodities()

		ts_capital = 10000
		vol_target = 0.4
		results = {}
		balance = 0
		start_capital = ts_capital * len(products)

		for product in tqdm.tqdm(products):
			loaded_prod = MarketDataLoader.load_datastream(product)
			size_policy = VolTargetInertiaPolicy(
				annual_vol_target=vol_target,
				trading_capital=ts_capital)

			tr_sys = TradingSystemIter(
				product=loaded_prod,
				trading_rules=[sma],
				forecast_weights=[1.],
				size_policy=size_policy
			)

			# simulation with constant risk
			tsar = tr_sys.run()

			results.update({product["name"]: tsar})
			balance += tsar.balance_delta()

		# plot whole balance
		results_list = [r for r in results.values()]
		account_df = pd.DataFrame({
			"Date": results_list[0].dates,
			"Balance": [0. for _ in results_list[0].dates]
		})

		risk_free = start_capital * ((1 + 0.05) ** 20 - 1)
		self.logger.info(f"starting capital : {start_capital}")
		self.logger.info(f"final balance : {balance}")
		self.logger.info(f"5% risk free : {risk_free}")

		for tsar in results_list:
			account_df["Balance"] += tsar.account_series
		account_plt = AccountPlotter(account_df)
		account_plt.save_png(f"data/residual/all_plot_vect.png")

		# plot tsar
		tsar_plotter = TsarPlotter({"pname": results})
		tsar_plotter.save_fig(export_folder="data/residual")
		return results_list


if __name__ == "__main__":
	unittest.main()
