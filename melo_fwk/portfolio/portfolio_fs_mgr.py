import json
from pathlib import Path
from typing import List

from melo_fwk.market_data.base_market_loader import BaseMarketLoader
from melo_fwk.portfolio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem

import glob

from melo_fwk.utils.generic_config_loader import GenericConfigLoader
from melo_fwk.utils.quantflow_factory import QuantFlowFactory

class PortfolioFsManager(BasePortfolioManager):

	def __init__(self):
		super().__init__()
		config_node = GenericConfigLoader.get_node(PortfolioFsManager.__name__)
		self.filepath = Path(config_node["location"])

	def save_portfolio_config(self, name: str, portfolio: BaseTradingSystem):
		self.logger.info(f"Dumping {name} to {self.filepath}/{name}.json")

		data_dict = portfolio.asdict()
		json_data = json.dumps(data_dict, indent=4)
		json_path = self.filepath / f"{name}.json"
		with open(json_path, "w") as fs:
			fs.write(json_data)

	def load_portfolio_config(self, market_mgr: BaseMarketLoader, name: str) -> BaseTradingSystem:
		file_glob = glob.glob(str(Path(self.filepath) / f"{name}*"))
		with open(file_glob[0], "r") as fs:
			result = json.load(fs)

		return BaseTradingSystem.from_dict(result, market_mgr)
