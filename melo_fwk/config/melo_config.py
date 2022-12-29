from typing import List, Type, Tuple, Dict, Union

from melo_fwk.config.config_helper import ConfigBuilderHelper
from melo_fwk.config.product_config import ProductConfigBuilder
from melo_fwk.config.strat_config import StratConfigRegistry, StrategyConfigBuilder
from melo_fwk.config.pose_size_config import SizePolicyConfigBuilder
from melo_fwk.config.estimator_config import EstimatorConfigBuilder
from melo_fwk.db.portfolio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.estimators.base_estimator import MeloBaseEstimator
# from melo_fwk.reporters.base_reporter import BaseReporter
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.pose_size import BaseSizePolicy

from pathlib import Path

from dataclasses import dataclass

import os

from melo_fwk.strategies import BaseStrategy
from melo_fwk.utils.weights import Weights


@dataclass(frozen=True)
class MeloConfig:
	name: str
	# {prod_name: Product}, start..end
	products_config: Tuple[dict, List[int]]
	size_policy: BaseSizePolicy
	strat_config_registry: StratConfigRegistry
	# (list(strats OR tuple(type(strat), param)), fw)
	strategies_config: Tuple[List[Union[BaseStrategy, Tuple[Type[BaseStrategy], Dict]]], Weights]
	# (estimator, **params)
	estimator_config_: Tuple[Type[MeloBaseEstimator], List[str]]
	reporter_class_: callable  # Type[BaseReporter]
	export_name: str

	@staticmethod
	def build_config(quant_query_path: Path, quant_query: dict):
		"""
		Should rework into config builder factory
		ex: parse strat vs strat metadata

		:param quant_query_path:
		:param quant_query:
		"""
		strat_config_registry = StratConfigRegistry.build_registry(str(quant_query_path.parent))
		return MeloConfig(
			name=ConfigBuilderHelper.strip_single(quant_query, "QueryName"),
			products_config=ProductConfigBuilder.build_products(quant_query),
			size_policy=SizePolicyConfigBuilder.build_size_policy(quant_query),
			strat_config_registry=strat_config_registry,
			strategies_config=StrategyConfigBuilder.build_strategy(quant_query, strat_config_registry),
			estimator_config_=EstimatorConfigBuilder.build_estimator(quant_query),
			reporter_class_=EstimatorConfigBuilder.get_reporter(quant_query),
			export_name=EstimatorConfigBuilder.get_export_name(quant_query)
		)

	def build_estimator(self):
		return self.estimator_config_[0](
			products=self.products_config[0],
			time_period=self.products_config[1],
			strategies=self.strategies_config[0],
			forecast_weights=self.strategies_config[1],
			size_policy=self.size_policy,
			estimator_params=self.estimator_config_[1]
		)

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

	def _check_export_directories(self, output_dir):
		if not os.path.isdir(output_dir):
			os.mkdir(output_dir)
		if not os.path.isdir(output_dir + "/data/"):
			os.mkdir(output_dir + "/data/")
		if not os.path.isdir(output_dir + "/data/" + self.name):
			os.mkdir(output_dir + "/data/" + self.name)
		if not os.path.isdir(output_dir + "/data/" + self.name + "/assets/"):
			os.mkdir(output_dir + "/data/" + self.name + "/assets/")

	def asdict(self):
		return {
			"products_config": self.products_config,
			"size_policy": self.size_policy,
			"strat_config_registry": self.strat_config_registry,
			"strategies_config": self.strategies_config,
			"estimator_config_": self.estimator_config_,
			"reporter_class_": self.reporter_class_,
			"export_name": self.export_name,
		}

	def __str__(self):
		return str(self.asdict())

	def export_trading_system(self, pf_mgr: BasePortfolioManager, name: str):
		"""should it take an exportMgr object as param for export ??"""
		if self.export_name is not None:
			# do the stuff here
			pf_mgr.save_portfolio_config(name, [self.build_estimator().build_trading_system_cluster()])
