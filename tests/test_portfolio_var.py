from melo_fwk.loggers.console_logger import ConsoleLogger
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.var.basket import VaRBasket
from melo_fwk.trading_systems import TradingSystemIter, TradingSystem

from melo_fwk.market_data import MarketDataLoader

from melo_fwk.strategies import EWMAStrategy
from melo_fwk.pose_size import VolTargetInertiaPolicy

from melo_fwk.plots.var_plot import VarPlotter
from melo_fwk.var.VaR import VaR99, VaR95
from melo_fwk.var.CVaR import CVaR

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

		# products = MarketDataLoader.get_fx()
		products = MarketDataLoader.get_commodities()
		products = [MarketDataLoader.load_datastream(p) for p in products[7:16]]
		# products = MarketDataLoader.sample_products(3)

		results = {}
		balance = 0
		start_capital = 10000 * len(products)
		tsar_list = []
		for product in tqdm.tqdm(products):
			# loaded_prod = MarketDataLoader.load_datastream(product)
			size_policy = VolTargetInertiaPolicy(
				annual_vol_target=0.3,
				trading_capital=start_capital)

			tr_sys = TradingSystemIter(
				# product=loaded_prod,
				product=product,  # .get_years([2007, 2008]),
				trading_rules=[sma],
				forecast_weights=[1.],
				size_policy=size_policy
			)

			# simulation with constant risk
			tsar = tr_sys.run()

			results.update({product.name: tsar})
			tsar_list.append(tsar)
			balance += tsar.balance_delta()

		lp = len(products)
		basket = VaRBasket(tsar_list, products, [1/lp]*lp)

		# VarPlotter.plot_prices(basket.simulate_hist(10, 0.9))
		# VarPlotter.plot_prices(basket.simulate_price(10, 10000))
		# VarPlotter.plot_price_paths(basket.simulate_price_paths(10, 10000), basket.tails)
		# VarPlotter.plot_price_paths(basket.simulate_hist_paths(10, 0.9), basket.tails)

		risk_free = start_capital * ((1 + 0.05) ** 20 - 1)
		self.logger.info(f"starting capital : {start_capital}")
		self.logger.info(f"final balance : {balance}")
		self.logger.info(f"5% risk free : {risk_free}")

		n_days = 10
		n_sim = 20000
		r_spl = 0.8

		var99 = VaR99(basket, n_days, n_sim, method="mc", gen_path=True)
		self.logger.info(f"VaR99 MC P : {var99}")

		var99 = VaR99(basket, n_days, n_sim, method="mc", gen_path=False)
		self.logger.info(f"VaR99 MC S : {var99}")

		var99 = VaR99(basket, n_days, r_spl, method="h", gen_path=True)
		self.logger.info(f"VaR99 H P: {var99}")

		var99 = VaR99(basket, n_days, r_spl, method="h", gen_path=False)
		self.logger.info(f"VaR99 H S: {var99}")



		var95 = VaR95(basket, n_days, n_sim, method="mc", gen_path=True)
		self.logger.info(f"VaR95 MC P : {var95}")

		var95 = VaR95(basket, n_days, n_sim, method="mc", gen_path=False)
		self.logger.info(f"VaR95 MC S: {var95}")

		var95 = VaR95(basket, n_days, r_spl, method="h", gen_path=True)
		self.logger.info(f"VaR95 H P : {var95}")

		var95 = VaR95(basket, n_days, r_spl, method="h", gen_path=False)
		self.logger.info(f"VaR95 H S: {var95}")



		cvar = CVaR(basket, n_days, n_sim, method="mc", gen_path=False)
		self.logger.info(f"ES MC S: {cvar}")

		cvar = CVaR(basket, n_days, n_sim, method="mc", gen_path=True)
		self.logger.info(f"ES MC P: {cvar}")

		cvar = CVaR(basket, n_days, r_spl, method="h", gen_path=False)
		self.logger.info(f"ES H S: {cvar}")

		cvar = CVaR(basket, n_days, r_spl, method="h", gen_path=True)
		self.logger.info(f"ES H P: {cvar}")

		# account_plt = AccountPlotter(account_df)
		# account_plt.save_png(f"data/residual/all_plot_vect.png")

		# plot tsar
		# tsar_plotter = TsarPlotter({"pname": results})
		# tsar_plotter.save_fig(export_folder="data/residual")
		# return results_list


if __name__ == "__main__":
	unittest.main()