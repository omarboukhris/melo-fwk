from melo_fwk.loggers.console_logger import ConsoleLogger
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.plots import AccountPlotter
from melo_fwk.basket.var_basket import VaRBasket
from minimelo.trading_systems import TradingSystemIter

from melo_fwk.market_data import MarketDataLoader

from minimelo.strategies import EWMAStrategy
from minimelo.pose_size import VolTargetInertiaPolicy

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
		# products = MarketDataLoader.get_commodities()
		# products = [MarketDataLoader.load_datastream(p) for p in products[7:16]]
		products = MarketDataLoader.sample_products(9)

		ts_capital = 10000
		results = []
		balance = 0
		start_capital = ts_capital * len(products)
		tsar_list = []
		for product in tqdm.tqdm(products):
			# loaded_prod = MarketDataLoader.load_datastream(product)
			size_policy = VolTargetInertiaPolicy(
				annual_vol_target=0.4,
				trading_capital=ts_capital)

			tr_sys = TradingSystemIter(
				# product=loaded_prod,
				product=product,  # .get_years([2007, 2008]),
				trading_rules=[sma],
				forecast_weights=[1.],
				size_policy=size_policy
			)

			# simulation with constant risk
			tsar = tr_sys.run()

			results.append(tsar)
			tsar_list.append(tsar)
			balance += tsar.balance_delta()


		risk_free = start_capital * ((1 + 0.05) ** 20 - 1)
		self.logger.info(f"starting capital : {start_capital}")
		self.logger.info(f"final balance : {balance}")
		self.logger.info(f"5% risk free : {risk_free}")

		account_df = pd.DataFrame({
			"Date": results[0].dates,
			"Balance": [0. for _ in results[0].dates]
		})
		for tsar in results:
			account_df["Balance"] += tsar.account_series
		account_plt = AccountPlotter(account_df)
		account_plt.save_png(f"data/residual/all_plot_vect.png")

		n_days = 1
		n_sim = 20000
		r_spl = 0.8
		lp = len(products)

		basket = VaRBasket(tsar_list, products, [1/lp]*lp)

		# VarPlotter.plot_prices(basket.simulate_hist(n_days, r_spl))
		# VarPlotter.plot_prices(basket.simulate_price(n_days, n_sim))
		# VarPlotter.plot_price_paths(basket.simulate_price_paths(n_days, n_sim), basket.tails)
		# VarPlotter.plot_price_paths(basket.simulate_hist_paths(n_days, r_spl), basket.tails)

		var99 = VaR99(basket, n_days, n_sim, method="mc", gen_path=True)
		self.logger.info(f"VaR99 MC P : {var99}")

		var99 = VaR99(basket, n_days, n_sim, method="mc", gen_path=False)
		self.logger.info(f"VaR99 MC S : {var99}")

		var99 = VaR99(basket, n_days, r_spl, method="h", gen_path=True)
		self.logger.info(f"VaR99 H P: {var99}")

		var99 = VaR99(basket, n_days, r_spl, method="h", gen_path=False)
		self.logger.info(f"VaR99 H S: {var99}")

		print("------------------------------------------")

		basket.reset_vol().static_vol_shock(0.2)
		var99 = VaR99(basket, n_days, n_sim, method="mc", gen_path=True)
		self.logger.info(f"VaR99 MC P : {var99}")

		var99 = VaR99(basket, n_days, n_sim, method="mc", gen_path=False)
		self.logger.info(f"VaR99 MC S : {var99}")

		print("------------------------------------------")

		basket.reset_vol().random_vol_shock(0.2, 0.05)
		var99 = VaR99(basket, n_days, n_sim, method="mc", gen_path=True)
		self.logger.info(f"VaR99 MC P : {var99}")

		var99 = VaR99(basket, n_days, n_sim, method="mc", gen_path=False)
		self.logger.info(f"VaR99 MC S : {var99}")

		print("------------------------------------------")

		basket.reset_vol()
		var95 = VaR95(basket, n_days, n_sim, method="mc", gen_path=True)
		self.logger.info(f"VaR95 MC P : {var95}")

		var95 = VaR95(basket, n_days, n_sim, method="mc", gen_path=False)
		self.logger.info(f"VaR95 MC S: {var95}")

		var95 = VaR95(basket, n_days, r_spl, method="h", gen_path=True)
		self.logger.info(f"VaR95 H P : {var95}")

		var95 = VaR95(basket, n_days, r_spl, method="h", gen_path=False)
		self.logger.info(f"VaR95 H S: {var95}")

		print("------------------------------------------")

		cvar = CVaR(basket, n_days, n_sim, method="mc", gen_path=False)
		self.logger.info(f"ES MC S: {cvar}")

		cvar = CVaR(basket, n_days, n_sim, method="mc", gen_path=True)
		self.logger.info(f"ES MC P: {cvar}")

		cvar = CVaR(basket, n_days, r_spl, method="h", gen_path=False)
		self.logger.info(f"ES H S: {cvar}")

		cvar = CVaR(basket, n_days, r_spl, method="h", gen_path=True)
		self.logger.info(f"ES H P: {cvar}")


if __name__ == "__main__":
	unittest.main()
