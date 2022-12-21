from typing import List

from melo_fwk.db_mgr.mongo_db_mgr import MongodbManager
from dataclasses import dataclass

from melo_fwk.market_data.product import Product
from minimelo.pose_size import BaseSizePolicy
from minimelo.strategies import BaseStrategy

from melo_fwk.utils.quantflow_factory import QuantFlowFactory

@dataclass(frozen=True)
class TradingSystemConfig:
	product: Product
	trading_rules: List[BaseStrategy]
	forecast_weights: List[float]
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
				"product": tsys.product.name,
				"trading_rules": [{
					type(x).__name__: x.to_dict()
					for x in tsys.trading_rules
				}],
				"forecast_weights": tsys.forecast_weights,
				"size_policy": type(tsys.size_policy).__name__,
				"vol_target": tsys.size_policy.vol_target.to_dict(),
			}

			self._mongo_mgr.insert_data(
				PortfoliodbManager.portfolio_table_name, data_dict)

	def load_portfolio_config(self, name: str):
		results = self._mongo_mgr.select_request(
			PortfoliodbManager.portfolio_table_name, {"name": name})

		for result in results:
			yield {
				"product": QuantFlowFactory.get_product(result["product"]),
				"trading_rules": [
					QuantFlowFactory.get_strategy(strat_)(**config)
					for strat_, config in result["trading_rules"]
				],
				"forecast_weights": result["forecast_weights"],
				"size_policy": QuantFlowFactory.get_size_policy(result["size_policy"])(
					**result["vol_target"]
				),
			}

