from pathlib import Path
from typing import List

from melo_fwk.db.market_data.market_data_mongo_loader import MarketDataMongoLoader
from melo_fwk.db.portfolio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.db.portfolio.portfolio_db_mgr import PortfoliodbManager
from melo_fwk.db.portfolio.portfolio_fs_mgr import PortfolioFsManager
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

	def save_portfolio_config(self, name: str, portfolio: List[BaseTradingSystem]):
		for pf_mgr in self.pf_mgr_list:
			try:
				return pf_mgr.save_portfolio_config(name, portfolio)
			except Exception as e:
				self.logger.warn(f"{type(pf_mgr).__name__} failed .save_portfolio_config() : {e}")
		raise Exception("(CompositePortfolioManager) All alternatives failed")

	def load_portfolio_config(self, mongo_market_mgr: MarketDataMongoLoader, name: str):
		for pf_mgr in self.pf_mgr_list:
			try:
				return pf_mgr.load_portfolio_config(mongo_market_mgr, name)
			except Exception as e:
				self.logger.warn(f"{type(pf_mgr).__name__} failed .load_portfolio_config() : {e}")
		raise Exception("(CompositePortfolioManager) All alternatives failed")
