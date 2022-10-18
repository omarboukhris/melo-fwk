import math

from melo_fwk.policies.vol_target_policies.vol_target import VolTarget
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TradingSystemAnnualResult:
	dates: pd.Series
	price_series: pd.Series
	forecast_series: pd.Series
	size_series: pd.Series
	account_series: pd.Series
	daily_pnl_series: pd.Series
	vol_target: VolTarget

	def get_metric_by_name(self, name: str, rf: float = 0.):
		if name in ["sharpe", "sr"]:
			return self.sharpe_ratio(rf)
		if name in ["sortino", "sor"]:
			return self.sortino_ratio(rf)
		if name in ["drawdown", "ddown"]:
			return self.max_drawdown()
		if name in ["calmar", "cr"]:
			return self.calmar_ratio()

	def compute_all_metrics(self, rf: float = 0.0):
		return {
			"Sharpe": self.sharpe_ratio(rf),
			"Sortino": self.sortino_ratio(rf),
			"MaxDrawdown": self.max_drawdown(),
			"Calmar": self.calmar_ratio(),
			"PnL": self.PnL(),
			"ReturnVolatility": self.return_vol()
		}

	def annual_delta(self):
		assert len(self.account_series) > 1, \
			"(TradingSystemAnnualReport) final_balance: account data frame is empty"
		return self.account_series.iloc[-1]

	def sharpe_ratio(self, rf: float = 0.0):
		mean = self.account_series.mean() - self.account_series.iat[0] - rf
		sigma = self.account_series.std()
		sharpe_r = mean / sigma if sigma != 0 else 0.
		return 0. if math.isnan(sharpe_r) else sharpe_r

	def sortino_ratio(self, rf: float = 0.0):
		# needs rework ########################
		pass

	def PnL(self):
		return self.account_series.iat[-1]

	def return_vol(self):
		return self.account_series.std()

	def get_drawdown(self, trading_days: int = 255):
		# this is bugged ########################
		peak = self.account_series.rolling(window=trading_days, min_periods=1).max()
		dd = (self.account_series / peak) - 1
		return dd

	def max_drawdown(self):
		return self.get_drawdown().min()

	def calmar_ratio(self):
		calmars = self.account_series.mean() / abs(self.max_drawdown())
		return calmars

