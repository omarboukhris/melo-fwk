from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from mutils.generic_config_loader import GenericConfigLoader
from mutils.mongo_db_mgr import MongodbManager
from melo_fwk.pfio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem


class PortfolioMongoManager(BasePortfolioManager):

	portfolio_table_name: str = "portfolio"

	def __init__(self):
		super().__init__()
		config = GenericConfigLoader.get_node(PortfolioMongoManager.__name__, {})
		dburl = config["dburl"]
		self.mongo_mgr = MongodbManager(dburl)

	def save_portfolio_config(self, name: str, portfolio: BaseTradingSystem):
		self.mongo_mgr.connect("tradingSytemConfig")
		data_dict = portfolio.asdict()

		self.mongo_mgr.insert_data(
			PortfolioMongoManager.portfolio_table_name, data_dict)

	def load_portfolio_config(self, market_mgr: BaseMarketLoader, name: str) -> BaseTradingSystem:
		self.mongo_mgr.connect("tradingSytemConfig")

		result = self.mongo_mgr.select_request(
			PortfolioMongoManager.portfolio_table_name, {"name": name})

		return BaseTradingSystem.from_dict(result, market_mgr)

	def book_exists(self, name: str) -> bool:
		self.mongo_mgr.connect("tradingSytemConfig")

		result = self.mongo_mgr.select_request(
			PortfolioMongoManager.portfolio_table_name, {"name": name})
		return result != {}
