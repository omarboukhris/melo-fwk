
from melo_fwk.metrics.metrics import AccountMetrics
from melo_fwk.policies.vol_target_policy import VolTarget
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class TradingSystemAnnualResult:
	account_metrics: AccountMetrics
	dates: pd.Series
	price_series: pd.Series
	forecast_series: pd.Series
	size_series: pd.Series
	account_series: pd.Series
	daily_pnl_series: pd.Series
	vol_target: VolTarget

	def annual_delta(self):
		assert len(self.account_series) > 1, \
			"(TradingSystemAnnualReport) final_balance: account data frame is empty"
		return self.account_series.iloc[-1]


