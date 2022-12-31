import json
from pathlib import Path
from typing import List

from melo_fwk.market_data.market_data_mongo_loader import MarketDataMongoLoader
from melo_fwk.portfolio.base_portfolio_mgr import BasePortfolioManager
from melo_fwk.trading_systems.base_trading_system import BaseTradingSystem

import glob

from melo_fwk.utils.quantflow_factory import QuantFlowFactory

class PortfolioFsManager(BasePortfolioManager):
	parent_folder = Path(Path(__file__).parent)
	portfolio_fs_name: str = "portfolio"

	def __init__(self, filepath: Path):
		super().__init__()
		if filepath is not None:
			self.filepath = filepath
		else:
			self.filepath = PortfolioFsManager.parent_folder / "assets"

	def save_portfolio_config(self, name: str, portfolio: List[BaseTradingSystem]):
		output = []
		for tsys in portfolio:
			data_dict = {
				"name": name,  # add trading sys name ??
				"product_basket": tsys.product_basket.to_dict(),
				"strat_basket": tsys.strat_basket.to_dict(),
				"size_policy": type(tsys.size_policy).__name__,
				"vol_target": tsys.size_policy.vol_target.to_dict(),
			}
			output.append(data_dict)

		# write json file
		self.logger.info(f"Dumping {name} to {self.filepath}/{name}.json")
		json_data = json.dumps(output, indent=4)
		json_path = self.filepath / f"{name}.json"
		with open(json_path, "w") as fs:
			fs.write(json_data)


	def load_portfolio_config(self, mongo_market_mgr: MarketDataMongoLoader, name: str):
		file_glob = glob.glob(str(Path(self.filepath) / f"{name}*"))
		results = []
		for filename in file_glob:
			with open(filename, "r") as fs:
				results.append(json.load(fs))

		for result in results:
			if result["name"] == name:
				self.logger.warn(f"(PortfolioFsManager) Portfolio names are different {result['name']} != {name}")

			yield {
				"product_basket": mongo_market_mgr.load_product_basket(result["product_basket"]),
				"strat_basket": QuantFlowFactory.build_strat_basket(result["strat_basket"]),
				"size_policy": QuantFlowFactory.get_size_policy(result["size_policy"])(
					**result["vol_target"]),
			}

