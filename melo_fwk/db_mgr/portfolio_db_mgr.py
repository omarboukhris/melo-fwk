from typing import List

from melo_fwk.basket.product_basket import ProductBasket
from melo_fwk.basket.start_basket import StratBasket
from melo_fwk.db_mgr.mongo_db_mgr import MongodbManager
from dataclasses import dataclass

from melo_fwk.market_data.product import Product
from melo_fwk.pose_size import BaseSizePolicy
from melo_fwk.strategies import BaseStrategy

from melo_fwk.utils.quantflow_factory import QuantFlowFactory
from melo_fwk.utils.weights import Weights


@dataclass(frozen=True)
class TradingSystemConfig:
	product_basket: ProductBasket
	strat_basket: StratBasket
	size_policy: BaseSizePolicy = BaseSizePolicy(0., 0.)

class PortfoliodbManager:
	_mongo_mgr: MongodbManager

	portfolio_table_name: str = "portfolio"

	def connect(self):
		self._mongo_mgr.connect()

	def close(self):
		self._mongo_mgr.close()

	def save_portfolio_config(self, name: str, portfolio: List[TradingSystemConfig]):
		for tsys in portfolio:
			data_dict = {
				"name": name,
				"product_basket": tsys.product_basket.to_dict(),
				"strat_basket": tsys.strat_basket.to_dict(),
				"size_policy": type(tsys.size_policy).__name__,
				"vol_target": tsys.size_policy.vol_target.to_dict(),
			}

			self._mongo_mgr.insert_data(
				PortfoliodbManager.portfolio_table_name, data_dict)

	def load_portfolio_config(self, guid: str):
		results = self._mongo_mgr.select_request(
			PortfoliodbManager.portfolio_table_name, {"guid": guid})

		for result in results:
			yield {
				"product_basket": None,  # load products in basket, Mongo data loader
				"strat_basket": QuantFlowFactory.build_strat_basket(result["strat_basket"]),
				"size_policy": QuantFlowFactory.get_size_policy(result["size_policy"])(
					**result["vol_target"]
				),
			}

