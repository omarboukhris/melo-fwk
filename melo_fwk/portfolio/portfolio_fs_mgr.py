import json
from pathlib import Path
from typing import List

from melo_fwk.market_data.base_market_loader import BaseMarketLoader
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

	def save_portfolio_config(self, name: str, portfolio: BaseTradingSystem):
		data_dict = {
			"name": name,  # add trading sys name ??
			"product_basket": portfolio.product_basket.to_dict(),
			"strat_basket": portfolio.strat_basket.to_dict(),
			"size_policy": type(portfolio.size_policy).__name__,
			"vol_target": portfolio.size_policy.vol_target.to_dict(),
		}

		# write json file
		self.logger.info(f"Dumping {name} to {self.filepath}/{name}.json")
		json_data = json.dumps(data_dict, indent=4)
		json_path = self.filepath / f"{name}.json"
		with open(json_path, "w") as fs:
			fs.write(json_data)


	def load_portfolio_config(self, mongo_market_mgr: BaseMarketLoader, name: str) -> BaseTradingSystem:
		file_glob = glob.glob(str(Path(self.filepath) / f"{name}*"))
		with open(file_glob[0], "r") as fs:
			result = json.load(fs)

		return BaseTradingSystem(
			name=result["name"],
			product_basket=mongo_market_mgr.load_product_basket(result["product_basket"]),
			strat_basket=QuantFlowFactory.build_strat_basket(result["strat_basket"]),
			size_policy=QuantFlowFactory.get_size_policy(result["size_policy"])(
				**result["vol_target"])
		)
