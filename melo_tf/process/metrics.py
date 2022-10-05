
import pandas as pd
import numpy as np
from dataclasses import dataclass

#debug this

@dataclass(frozen=True)
class AccountMetrics:
	account_df: pd.Series

	def sharpe_ratio(self, rf: float = 0.0):
		trading_days = len(self.account_df)
		mean = self.account_df.mean() * trading_days - rf
		sigma = self.account_df.std() * np.sqrt(trading_days)
		return mean / sigma

	def sortino_ratio(self, rf: float = 0.0):
		trading_days = len(self.account_df)
		mean = self.account_df.mean() * trading_days - rf
		std_neg = self.account_df[self.account_df < 0].std() * np.sqrt(trading_days)
		return mean / std_neg

	def PnL(self):
		return self.account_df.iat[-1]

	def return_vol(self):
		trading_days = len(self.account_df)
		return self.account_df.std() * np.sqrt(trading_days)

	def get_drawdown(self):
		comp_ret = (self.account_df + 1).cumprod()
		peak = comp_ret.expanding(min_periods=1).max()
		dd = (comp_ret / peak) - 1
		return dd

	def max_drawdown(self):
		return self.get_drawdown().min()

	def calmar_ratio(self):
		trading_days = len(self.account_df)
		calmars = self.account_df.mean() * trading_days / abs(self.max_drawdown())
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
