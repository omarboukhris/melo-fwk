from math import sqrt
from typing import List

import numpy as np
import pandas as pd

from melo_fwk.datastreams.base_datastream import BaseDataStream

"""This class is used to wrap Tsar Data Frames in an interface"""
# TradingResult
class TsarDataStream(BaseDataStream):
	
	def __init__(self, **kwargs):
		self.name = kwargs.pop("name")
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
			date_label=self.date_label
		)
		return tsar

	def get_year(self, y: int):
		# offset account with start capital
		# useful when running whole history with the same vol target
		tsar = TsarDataStream(
			name=self.name,
			dataframe=self.dataframe.loc[
				self.dataframe["Year"] == y,
			].reset_index(drop=True),
			date_label=self.date_label,
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
		pct_returns = self.account_series.pct_change().dropna()
		n_days = len(pct_returns)
		mean = (pct_returns.mean() * n_days) - rf
		sigma = pct_returns.std() * sqrt(n_days)
		sharpe_r = mean / sigma if sigma != 0 else mean
		return sharpe_r

	def gar(self):
		pct_returns = self.account_series.pct_change().replace([np.inf, -np.inf], np.nan).dropna().abs()
		non_zero_pct = pct_returns[pct_returns != 0]
		geomean = np.exp(np.log(non_zero_pct).mean())
		return geomean

	def sortino_ratio(self, rf: float = 0.0):
		pct_returns = self.account_series.pct_change().dropna()
		n_days = len(pct_returns)
		mean = (pct_returns.mean() * n_days) - rf
		sigma = pct_returns[pct_returns < 0].std() * sqrt(n_days)
		sortino = mean / sigma if sigma != 0 else mean
		return sortino

	def last_pose(self):
		return self.size_series.iat[-1]

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
		pct_returns = self.account_series.pct_change().dropna()
		n_days = len(pct_returns)
		calmar = pct_returns.mean() * n_days / abs(self.max_drawdown())
		return calmar
