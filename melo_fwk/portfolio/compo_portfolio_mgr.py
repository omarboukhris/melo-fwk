import json
from pathlib import Path
from typing import List

from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.portfolio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.portfolio.portfolio_db_mgr import PortfoliodbManager
from melo_fwk.portfolio.portfolio_fs_mgr import PortfolioFsManager
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem


class CompositePortfolioManager(BasePortfolioManager):

	def __init__(self, pf_mgr_list: List[BasePortfolioManager]):
		super().__init__()
		self.pf_mgr_list = pf_mgr_list

	@staticmethod
	def with_mongo_first(dburl: str, fallback_path: str):
		return CompositePortfolioManager(
			pf_mgr_list=[
				PortfoliodbManager(dburl),
				PortfolioFsManager(Path(fallback_path)),
			]
		)

	@staticmethod
	def with_mongo_second(dburl: str, fallback_path: str):
		return CompositePortfolioManager(
			pf_mgr_list=[
				PortfolioFsManager(Path(fallback_path)),
				PortfoliodbManager(dburl),
			]
		)

	def save_portfolio_config(self, name: str, portfolio: BaseTradingSystem):
		for pf_mgr in self.pf_mgr_list:
			try:
				return pf_mgr.save_portfolio_config(name, portfolio)
			except Exception as e:
				self.logger.warn(f"{type(pf_mgr).__name__} failed .save_portfolio_config() : {e}")
		raise Exception("(CompositePortfolioManager) All alternatives failed")

	def load_portfolio_config(self, mongo_market_mgr: BaseMarketLoader, name: str) -> BaseTradingSystem:
		for pf_mgr in self.pf_mgr_list:
			# try:
			return pf_mgr.load_portfolio_config(mongo_market_mgr, name)
			# except Exception as e:
			# 	self.logger.warn(f"{type(pf_mgr).__name__} failed .load_portfolio_config() : {e}")
		raise Exception("(CompositePortfolioManager) All alternatives failed")

	@staticmethod
	def from_config(config_path: str):
		with open(config_path, "r") as fs:
			out = json.load(fs)
		pf_loaders = [
			PortfoliodbManager(out["dburl"]),
			PortfolioFsManager(Path(out["fallback_path"])),
		]
		if not out["mongo_first"]:
			pf_loaders.reverse()
		return CompositePortfolioManager(pf_loaders)
