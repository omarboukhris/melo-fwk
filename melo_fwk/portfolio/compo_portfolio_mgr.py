import json
from pathlib import Path
from typing import List

from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.portfolio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.portfolio.portfolio_db_mgr import PortfolioMongoManager
from melo_fwk.portfolio.portfolio_fs_mgr import PortfolioFsManager
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem
from melo_fwk.utils.quantflow_factory import QuantFlowFactory


class CompositePortfolioManager(BasePortfolioManager):

	def __init__(self, pf_mgr_list: List[BasePortfolioManager]):
		super().__init__()
		self.pf_mgr_list = pf_mgr_list

	def save_portfolio_config(self, name: str, portfolio: BaseTradingSystem):
		for pf_mgr in self.pf_mgr_list:
			try:
				return pf_mgr.save_portfolio_config(name, portfolio)
			except Exception as e:
				self.logger.warn(f"{type(pf_mgr).__name__} failed .save_portfolio_config() : {e}")
		raise Exception("(CompositePortfolioManager) All alternatives failed")

	def load_portfolio_config(self, market_mgr: BaseMarketLoader, name: str) -> BaseTradingSystem:
		for pf_mgr in self.pf_mgr_list:
			# try:
			return pf_mgr.load_portfolio_config(market_mgr, name)
			# except Exception as e:
			# 	self.logger.warn(f"{type(pf_mgr).__name__} failed .load_portfolio_config() : {e}")
		raise Exception("(CompositePortfolioManager) All alternatives failed")

	@staticmethod
	def from_config(pf_config: List[str]):
		pf_loaders = [QuantFlowFactory.get_pf_loader(pf) for pf in pf_config]
		return CompositePortfolioManager(pf_loaders)
