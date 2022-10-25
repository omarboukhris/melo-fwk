import pandas as pd
import tqdm

from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.market_data.product import Product
from melo_fwk.strategies import BaseStrategy
from melo_fwk.size_policies import BaseSizePolicy
from melo_fwk.size_policies.vol_target import VolTarget


from typing import List

class ClustersEstimator:

	def __init__(
		self,
		products: dict,
		time_period: List[int],
		strategies: List[BaseStrategy] = None,
		forecast_weights: List[int] = None,
		vol_target: VolTarget = VolTarget(0., 0.),
		size_policy_class_: callable = BaseSizePolicy,
		estimator_params: List[str] = None
	):
		self.logger = GlobalLogger.build_composite_for("ClustersEstimator")

		strategies = [] if strategies is None else strategies
		forecast_weights = [] if forecast_weights is None else forecast_weights
		assert len(strategies) == len(forecast_weights), self.logger.error(
			"Strategies and Forecast weight do not correspond.")

		self.products = products
		self.time_period = time_period
		self.strategies = strategies
		self.forecast_weights = forecast_weights
		self.vol_target = vol_target
		self.size_policy_class_ = size_policy_class_
		self.global_corr = "glob" in estimator_params

		self.logger.info("Estimator Initialized")

	def run(self):
		"""
		if global_corr:
			get global returns in dataframe
			compute corr heat map from df
		else :
			simulate all in one go,
			loop through range(timeperiod) :
			get yearly returns in dataframe
			compute corr heat map from df

		:return:
		"""
		out_dict = dict()
		# doesn't actually matter with buy and hold
		if self.global_corr:
			_trade_fn = self._trade_product_global
		else:
			_trade_fn = self._trade_product

		self.logger.info("Fetching products returns")
		for product_name, product in tqdm.tqdm(self.products.items(), leave=False):
			for year, y_return in _trade_fn(product).items():
				if year in out_dict.keys():
					out_dict[year].update(y_return)
				else:
					out_dict[year] = y_return

		self.logger.info("Building yearly correllation heatmap")
		df_dict = dict()
		for year, returns in out_dict.items():
			df_dict[year] = pd.DataFrame(returns).corr()

		return df_dict

	def _trade_product(self, product: Product):

		vol_target = VolTarget(
			annual_vol_target=self.vol_target.annual_vol_target,
			trading_capital=self.vol_target.trading_capital)
		size_policy = self.size_policy_class_(risk_policy=vol_target)

		trading_subsys = TradingSystem(
			product=product,
			trading_rules=self.strategies,
			forecast_weights=self.forecast_weights,
			size_policy=size_policy
		)

		tsar = trading_subsys.run()
		results = dict()
		for year in range(int(self.time_period[0]), int(self.time_period[1])):
			y_return = tsar.get_data_by_year(year).account_series
			if year in results.keys():
				results[year].update({product.name: y_return})
			else:
				results[year] = {product.name: y_return}

		return results

	def _trade_product_global(self, product: Product):
		vol_target = VolTarget(
			annual_vol_target=self.vol_target.annual_vol_target,
			trading_capital=self.vol_target.trading_capital)
		size_policy = self.size_policy_class_(risk_policy=vol_target)

		results = dict()
		for year in range(int(self.time_period[0]), int(self.time_period[1])):
			trading_subsys = TradingSystem(
				product=product.datastream.get_data_by_year(year),
				trading_rules=self.strategies,
				forecast_weights=self.forecast_weights,
				size_policy=size_policy
			)

			tsar = trading_subsys.run()
			y_return = tsar.get_data_by_year(year).account_series
			if year in results.keys():
				results[year].update({product.name: y_return})
			else:
				results[year] = {product.name: y_return}

		return results
