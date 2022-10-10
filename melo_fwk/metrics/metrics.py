
import pandas as pd
import numpy as np
from dataclasses import dataclass

@dataclass(frozen=True)
class AccountMetrics:
	account_df: pd.Series

	def sharpe_ratio(self, rf: float = 0.0):
		mean = self.account_df.mean() - self.account_df.iat[0] - rf
		sigma = self.account_df.std()
		return mean / sigma

	def sortino_ratio(self, rf: float = 0.0):
		# needs rework ########################
		mean = self.account_df.mean() - rf
		std_neg = self.account_df[self.account_df < 0].std()
		return mean / std_neg
		# rf_account = np.minimum(0, self.account_df - self.account_df.iat[0] - rf)**2
		# rf_account_mean = rf_account.mean()
		# mean = self.account_df.mean() - rf
		# return mean / rf_account_mean

	def PnL(self):
		return self.account_df.iat[-1]

	def return_vol(self):
		return self.account_df.std()

	def get_drawdown(self):
		# this is bugged ########################
		comp_ret = (self.account_df + 1).cumprod()
		peak = comp_ret.expanding(min_periods=1).max()
		dd = (comp_ret / peak) - 1
		return dd

	def max_drawdown(self):
		return self.get_drawdown().min()

	def calmar_ratio(self):
		calmars = self.account_df.mean() / abs(self.max_drawdown())
		return calmars

	@staticmethod
	def compute_all_metrics(series: pd.Series, rf: float = 0.0):
		account_metrics = AccountMetrics(series)
		return {
			"Sharpe": account_metrics.sharpe_ratio(rf),
			"Sortino": account_metrics.sortino_ratio(rf),
			"MaxDrawdown": account_metrics.max_drawdown(),
			"Calmar": account_metrics.calmar_ratio(),
			"PnL": account_metrics.PnL(),
			"ReturnVolatility": account_metrics.return_vol()
		}
