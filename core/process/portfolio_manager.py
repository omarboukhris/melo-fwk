
from trading_system import TradingSystem
from typing import List

class PortfolioManager:

	def __init__(
		self,
		trading_systems: List[TradingSystem]
	):
		self.trading_systems = trading_systems

	def process_trades(self):
		for trading_sys in self.trading_systems:
			while not trading_sys.simulation_ended():
				trading_sys.trade_next()



