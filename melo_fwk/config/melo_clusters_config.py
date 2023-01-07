import os
from dataclasses import dataclass
from typing import List, Tuple

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.start_basket import StratBasket
from melo_fwk.config.config_helper import ConfigBuilderHelper
from melo_fwk.config.estimator_config import EstimatorConfigBuilder
from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.portfolio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.pose_size import BaseSizePolicy
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.trading_systems import TradingSystem
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.utils.weights import Weights


@dataclass(frozen=True)
class MeloClustersConfig:
	name: str
	product_baskets: List[ProductBasket]
	strats_list: List[StratBasket]
	pose_size_list: List[BaseSizePolicy]
	reporter_class_: callable  # Type[BaseReporter]
	# add estimator

	def __post_init__(self):
		assert len(self.product_baskets) == len(self.strats_list), \
			f"len product != strat ({len(self.product_baskets)} != {len(self.strats_list)})"
		assert len(self.product_baskets) == len(self.pose_size_list), \
			f"len product != size_policy ({len(self.product_baskets)} != {len(self.pose_size_list)})"

	def build_trading_systems(self):
		return [
			TradingSystem(product_basket=p_basket, strat_basket=s_basket, size_policy=size_policy)
			for p_basket, s_basket, size_policy in zip(self.product_baskets, self.strats_list, self.pose_size_list)
		]

	@staticmethod
	def build_config(pf_mgr: BasePortfolioManager, market_db: BaseMarketLoader, quant_query: dict):
		clusters, weights = MeloClustersConfig.load_clusters(pf_mgr, market_db, quant_query)
		return MeloClustersConfig(
			name=ConfigBuilderHelper.strip_single(quant_query, "QueryName"),
			product_baskets=[c.product_basket for c in clusters],
			strats_list=[c.strat_basket for c in clusters],
			pose_size_list=[c.size_policy for c in clusters],
			reporter_class_=EstimatorConfigBuilder.get_reporter(quant_query),
		)

	@staticmethod
	def load_clusters(
		pf_mgr: BasePortfolioManager,
		market_db: BaseMarketLoader,
		quant_query: dict
	) -> Tuple[List[BaseTradingSystem], Weights]:

		clusters_dict = ConfigBuilderHelper.strip_single(quant_query, "Clusters")
		clusters_name = [s.strip() for s in ConfigBuilderHelper.strip_single(clusters_dict, "AlphanumList").split(",")]
		clusters_weights = [float(s) for s in ConfigBuilderHelper.strip_single(clusters_dict, "WeightsList").split(",")]
		clusters_divmult = float(ConfigBuilderHelper.strip_single(clusters_dict, "DivMult"))

		weights = Weights(
			weights=clusters_weights,
			divmult=clusters_divmult
		)

		clusters = [
			pf_mgr.load_portfolio_config(market_db, c_name)
			for c_name in clusters_name
		]
		return clusters, weights

	def build_clusters_estimator(self):
		"""This is next : Make BaseClusterEstimator to run :
			VaR
			Wei optim
			Vol Target
		Note: make var estim for singles
		"""
		raise NotImplemented


	def _check_export_directories(self, output_dir):
		if not os.path.isdir(output_dir):
			os.mkdir(output_dir)
		if not os.path.isdir(output_dir + "/data/"):
			os.mkdir(output_dir + "/data/")
		if not os.path.isdir(output_dir + "/data/" + self.name):
			os.mkdir(output_dir + "/data/" + self.name)
		if not os.path.isdir(output_dir + "/data/" + self.name + "/assets/"):
			os.mkdir(output_dir + "/data/" + self.name + "/assets/")

	def write_report(self, estimator_results: dict, output_dir: str = "./"):
		"""
		NOTE: Generates artifacts (
			export folder: $query_name/report.md
			assets folder: $query_name/assets/*.png
		)
		:param estimator_results:
		:param output_dir:
		:return:
		"""
		reporter = self.reporter_class_(self)
		md_ss = reporter.header()
		self._check_export_directories(output_dir)
		md_ss += reporter.process_results(output_dir, "/data/" + self.name, estimator_results)
		MdFormatter.save_md(output_dir + "/data/" + self.name, "report.md", md_ss)

