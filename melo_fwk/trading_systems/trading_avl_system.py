from melo_fwk.policies.vol_target_policies.vol_target import VolTarget
from melo_fwk.trading_systems.trading_vect_system import TradingVectSystem

import numpy as np
import pandas as pd

# AVL : Adaptative Vol Target
class TradingAVLSystem(TradingVectSystem):

	def __init__(self, **kwargs):
		super(TradingAVLSystem, self).__init__(**kwargs)
		self.size_policy.update_datastream(self.data_source)

	def run(self):

		forecast_series = self.forecast_cumsum()
		current_vol_target = self.size_policy.risk_policy
		pose_list, pnl_list = [], []
		for _, forecast in zip(self.data_source, forecast_series):
			pose_size = self.size_policy.position_size(forecast)
			pnl = self.data_source.get_current_diff() * pose_size
			updated_balance = current_vol_target.trading_capital + pnl
			adjusted_vol_target = current_vol_target.annual_cash_vol_target() / updated_balance
			current_vol_target = VolTarget(
				annual_vol_target=adjusted_vol_target,
				trading_capital=updated_balance,
			)

			pose_list.append(pose_size)
			pnl_list.append(pnl)

		pose_series = pd.Series(pose_list)
		daily_pnl = pd.Series(pnl_list)
		# orderbook building ??

		self.tsar_history = {
			"Date": self.data_source.get_dates(),
			"Price": self.data_source.get_close(),
			"Forecast": forecast_series,
			"PositionSize": pose_series,
			"Daily_PnL": daily_pnl
		}

