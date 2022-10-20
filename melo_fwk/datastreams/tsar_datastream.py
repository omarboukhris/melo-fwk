import melo_fwk.datastreams.utils.common as common

from melo_fwk.datastreams.base_datastream import BaseDataStream

from dataclasses import dataclass

import pandas as pd


"""This class is used to wrap Tsar Data Frames in an interface and to offer some HLOC operations"""
class TsarDataStream(BaseDataStream):
	
	def __init__(self, **kwargs):
		super(TsarDataStream, self).__init__(**kwargs)

	def get_data_by_year(self, y: str):
		return TsarDataStream(
			dataframe=self.dataframe.loc[
				self.dataframe["Year"] == y,
			].reset_index(drop=True),
			date_label=self._date_label,
		)

	def to_tsar(self):
		return TradingSystemAnnualResult(
			dates=self.dataframe["Date"],
			price_series=self.dataframe["Price"],
			forecast_series=self.dataframe["Forecast"],
			size_series=self.dataframe["Size"],
			account_series=self.dataframe["Account"],
			daily_pnl_series=self.dataframe["Daily_PnL"]
		)

@dataclass(frozen=True)
class TradingSystemAnnualResult:
	dates: pd.Series
	price_series: pd.Series
	forecast_series: pd.Series
	size_series: pd.Series
	account_series: pd.Series
	daily_pnl_series: pd.Series

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

	def to_datastream(self):
		tsar_df = pd.DataFrame({
			"Date": self.dates,
			"Price": self.price_series,
			"Forecast": self.forecast_series,
			"Size": self.size_series,
			"Account": self.account_series,
			"Daily_PnL": self.daily_pnl_series
		})
		return TsarDataStream(dataframe=tsar_df)

	def annual_delta(self) -> float:
		if len(self.account_series) < 1:
			return 0.
		return float(self.account_series.iloc[-1])

	def sharpe_ratio(self, rf: float = 0.0):
		mean = self.account_series.mean() - rf
		sigma = self.account_series.std()
		sharpe_r = mean / sigma if sigma != 0 else 0.
		return sharpe_r

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




