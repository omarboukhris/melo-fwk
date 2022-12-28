from typing import List

from melo_fwk.db_mgr.market_data_mongo_loader import MarketDataMongoLoader
from melo_fwk.db_mgr.mongo_db_mgr import MongodbManager
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem

from melo_fwk.utils.quantflow_factory import QuantFlowFactory


class PortfoliodbManager(MongodbManager):

	portfolio_table_name: str = "portfolio"

	def __init__(self, dburl: str = "mongodb://localhost:27017/"):
		super().__init__(dburl)

	def save_portfolio_config(self, guid: str, portfolio: List[BaseTradingSystem]):
		for tsys in portfolio:
			data_dict = {
				"guid": guid,
				"product_basket": tsys.product_basket.to_dict(),
				"strat_basket": tsys.strat_basket.to_dict(),
				"size_policy": type(tsys.size_policy).__name__,
				"vol_target": tsys.size_policy.vol_target.to_dict(),
			}

			self.insert_data(
				PortfoliodbManager.portfolio_table_name, data_dict)

	def load_portfolio_config(self, mongo_market_mgr: MarketDataMongoLoader, guid: str):
		results = self.select_request(
			PortfoliodbManager.portfolio_table_name, {"guid": guid})

		for result in results:
			yield {
				"product_basket": mongo_market_mgr.load_product_basket(result["product_basket"]),
				"strat_basket": QuantFlowFactory.build_strat_basket(result["strat_basket"]),
				"size_policy": QuantFlowFactory.get_size_policy(result["size_policy"])(
					**result["vol_target"]
				),
			}

