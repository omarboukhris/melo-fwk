from abc import ABC, abstractmethod

from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem


class BasePortfolioManager(ABC):

	def __init__(self):
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)

	@abstractmethod
	def save_portfolio_config(self, name: str, portfolio: BaseTradingSystem):
		...

	@abstractmethod
	def load_portfolio_config(self, mongo_market_mgr: BaseMarketLoader, name: str) -> BaseTradingSystem:
		...
