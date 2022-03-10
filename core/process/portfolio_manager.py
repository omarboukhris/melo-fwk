import pandas as pd

from trading_system import TradingSystem
from typing import List

class PortfolioManager:

	def __init__(
		self,
		trading_systems: List[TradingSystem]
	):
		self.trading_systems = trading_systems

	def process_trades(self):
		dates_set = set()

		for trading_sys in self.trading_systems:
			# loop through systems and run simulations
			while not trading_sys.simulation_ended():
				trading_sys.trade_next()

			# save dates to easily merge results
			for dates in trading_sys.get_account_history()["Dates"]:
				dates_set.add(dates)

		# post-processing and output dataframe setup
		dates_set = list(dates_set)
		dates_set.sort()
		df = pd.DataFrame()
		df["Date"] = dates_set
		df["Sum"] = 0

		# data merging
		for trading_sys in self.trading_systems:
			for idx, account in trading_sys.get_account_history().iterrows():
				df.loc[df["Date"] == account["Date"], "Balance"] += account["Balance"]


