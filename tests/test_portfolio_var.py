from melo_fwk.basket.start_basket import StratBasket
from melo_fwk.loggers.console_logger import ConsoleLogger
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.plots import AccountPlotter
from melo_fwk.basket.var_basket import VaRBasket
from melo_fwk.market_data.compo_market_loader import CompositeMarketLoader

from melo_fwk.trading_systems import TradingSystemIter
from melo_fwk.strategies import EWMAStrategy
from melo_fwk.pose_size import VolTargetInertiaPolicy
from melo_fwk.utils.weights import Weights

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

		strat_bsk = StratBasket(
			strat_list=[sma],
			weights=Weights([1.], 1.)
		)

		market = CompositeMarketLoader.from_config("tests/rc/loader_config.json")
		products = market.sample_products(9)

		ts_capital = 10000
		results = []
		balance = 0
		start_capital = ts_capital * len(products)
		size_policy = VolTargetInertiaPolicy(
			annual_vol_target=0.4,
			trading_capital=ts_capital)

		tr_sys = TradingSystemIter(
			strat_basket=strat_bsk,
			size_policy=size_policy
		)

		for product in tqdm.tqdm(products):
			tsar = tr_sys.run_product(product)

			results.append(tsar)
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

		basket = VaRBasket(results, products)

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
