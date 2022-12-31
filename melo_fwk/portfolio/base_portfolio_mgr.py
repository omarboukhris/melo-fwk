from typing import List

from melo_fwk.market_data.market_data_mongo_loader import MarketDataMongoLoader
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem


class BasePortfolioManager:

	def __init__(self):
		self.logger = GlobalLogger.build_composite_for(type(self).__name__)

	def save_portfolio_config(self, name: str, portfolio: List[BaseTradingSystem]):
		raise NotImplemented

	def load_portfolio_config(self, mongo_market_mgr: MarketDataMongoLoader, name: str):
		raise NotImplemented
