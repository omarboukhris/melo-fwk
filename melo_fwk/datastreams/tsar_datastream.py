import numpy as np
import pandas as pd

from melo_fwk.datastreams.base_datastream import BaseDataStream


"""This class is used to wrap Tsar Data Frames in an interface and to offer some HLOC operations"""
# TradingSystemAnnualResult
class TsarDataStream(BaseDataStream):
	
	def __init__(self, **kwargs):
		super(TsarDataStream, self).__init__(**kwargs)
		self.dates = self.dataframe["Date"]
		self.price_series = self.dataframe["Price"]
		self.forecast_series = self.dataframe["Forecast"]
		self.size_series = self.dataframe["Size"]
		self.account_series = self.dataframe["Account"]
		self.daily_pnl_series = self.dataframe["Daily_PnL"]

	def add(self, other):
		tsar = TsarDataStream(
			dataframe=pd.concat([self.dataframe, other.dataframe]).reset_index(drop=True),
			date_label=self._date_label
		)
		return tsar

	def get_year(self, y: int):
		# offset account with start capital
		# useful when running whole history with the same vol target
		tsar = TsarDataStream(
			dataframe=self.dataframe.loc[
				self.dataframe["Year"] == y,
			].reset_index(drop=True),
			date_label=self._date_label,
		)
		tsar._offset_account()
		return tsar

	def _offset_account(self):
		self.dataframe["Account"] -= self.account_series.iat[0]
		self.account_series -= self.account_series.iat[0]


	def get_metric_by_name(self, name: str, rf: float = 0.):
		if name in ["pnl", "PnL"]:
			return self.pnl()
		if name in ["sharpe", "sr", "Sharpe"]:
			return self.sharpe_ratio(rf)
		if name in ["sortino", "sor", "Sortino"]:
			return self.sortino_ratio(rf)
		if name in ["drawdown", "ddown", "MaxDrawdown"]:
			return self.max_drawdown()
		if name in ["calmar", "cr", "Calmar"]:
			return self.calmar_ratio()
		if name in ["vol", "ReturnVolatility"]:
			return self.return_vol()

	def compute_all_metrics(self, rf: float = 0.0):
		return {
			"Sharpe": self.sharpe_ratio(rf),
			"Sortino": self.sortino_ratio(rf),
			"MaxDrawdown": self.max_drawdown(),
			"Calmar": self.calmar_ratio(),
			"PnL": self.pnl(),
			"ReturnVolatility": self.return_vol()
		}

	def balance_delta(self) -> float:
		if len(self.account_series) < 1:
			return 0.
		return float(self.account_series.iloc[-1])

	def sharpe_ratio(self, rf: float = 0.0):
		mean = self.daily_pnl_series.mean() - rf
		sigma = self.daily_pnl_series.std()
		# pct_returns = self.account_series.diff()/self.account_series
		# mean = pct_returns.mean()
		# sigma = pct_returns.std()
		sharpe_r = mean / sigma if sigma != 0 else mean
		return sharpe_r

	def gar(self, starting_capital: float):
		avg_daily_diff = self.daily_pnl_series.mean()
		diff = avg_daily_diff / starting_capital
		a = (1 + diff).prod() ** 0.5 - 1.
		return a

	def sortino_ratio(self, rf: float = 0.0):
		mean = self.daily_pnl_series.mean() - rf
		sigma = self.daily_pnl_series[self.daily_pnl_series < 0].std()
		sortino = mean / sigma if sigma != 0 else mean
		return sortino

	def pnl(self):
		return self.account_series.iat[-1]

	def return_vol(self):
		return self.daily_pnl_series.std()

	def get_drawdown(self, trading_days: int = 255):
		peak = self.account_series.rolling(window=trading_days, min_periods=1).max()
		dd = (self.account_series - peak)  # - 1
		return dd.replace([np.inf, -np.inf], np.nan).fillna(0)

	def max_drawdown(self):
		return self.get_drawdown().min()

	def calmar_ratio(self):
		calmars = self.account_series.mean() / abs(self.max_drawdown())
		return calmars
