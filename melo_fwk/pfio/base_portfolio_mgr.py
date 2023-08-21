
from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem


class BasePortfolioManager:

	def __init__(self):
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)

	def save_portfolio_config(self, name: str, portfolio: BaseTradingSystem):
		raise NotImplementedError

	def load_portfolio_config(self, market_mgr: BaseMarketLoader, name: str) -> BaseTradingSystem:
		raise NotImplementedError
