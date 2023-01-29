# Melo Framework

This project is a work in progress

## Getting started

This project is a quantitative trading backtest ecosystem.

## Name

Melo-fwk and Melo-ql, respectively melo framework and melo query language

## Description

Melo-fwk & Melo-ql form a backtesting ecosystem used for trading simulations, quantitative strategy design and portfolio building.
Strategies and trading policies can easily be extended (WIP).

## Installation

pip install dependencies then pip install this repo

### Requirements

pandas, matplotlib, yfinance, numpy, pyparse, scikit-optimize, mongodb, scikit-learn, scipy

### Project status
Work In Progress

## MeloQL Usage

Tutorial on Mql is cooking

## Melo-Fwk Usage

### Run Backtest

```python
# import necessary packages
from melo_fwk.market_data import CommodityDataLoader
from minimelo.trading_systems import TradingSystem
from minimelo.strategies import EWMAStrategy
from minimelo.pose_size import VolTargetInertiaPolicy
from melo_fwk.plots import TsarPlotter

# fetch product
product = CommodityDataLoader.Gold

# setup strategy & strategy weight
strats = [
	EWMAStrategy(
		fast_span=16,
		slow_span=64,
		scale=16.,
	),
]
strat_weights = [1.]

# setup balance
balance = 60000

# setup size_policy
size_policy = VolTargetInertiaPolicy(
	annual_vol_target=0.25,
	trading_capital=balance)

# init trading system
trading_subsys = TradingSystem(
	product=product,
	trading_rules=strat,
	forecast_weights=fw,
	size_policy=size_policy
)

# run trading system for each year
#  and save result in dictionary
results = {
	f"Gold_{year}": trading_subsys.run_year(year)
	for year in product.years()
}

# update balance
balance += np.sum([tsar.annual_delta() for tsar in results.values()])
print(f"Final balance = {balance}")

# save annual metrics plots in export folder (make sure folder exists)
tsar_plotter.save_fig(export_folder="data/residual", mute=True)
```

### Add Data Loader

### Add Strategy

To add a new Strategy in the strategy stack, you need to follow a couple of steps.
First of all, we define the strategy :

```python
# import base class, dataclass and other necessary packages
from minimelo.strategies import BaseStrategy
from dataclasses import dataclass

import pandas as pd
import numpy as np


# define optimisation search space
# used by StratOptimEstimator to optimize strategies
@dataclass
class StratParamSpace:
	fast_span: int
	slow_span: int

	search_space = {
		"fast_span": [i for i in range(4, 60)],
		"slow_span": [i for i in range(30, 100)],
	}


# define the actual strategy component
# needs to inherit base and search space classes
@dataclass
class NewStrategy(BaseStrategy, StratParamSpace):

	# forecast_vect implements the computation 
	# of all forecast series from price data
	def forecast_vect(self, data: pd.Series) -> pd.Series:
		pass  # do your calculations here
```

This component on it's own is sufficient to be used in a harcoded backtesting scenario.
If we want to link it to mql and use it in that context, we need to register the component in the factory

```python
# in melo_fwk.quantfactory_registry

# find register_strats() and register_search_spaces funtions 
def register_strats():
	# register strategy in strategy stack
	quantflow_factory.QuantFlowFactory.register_strategy("NewStrategy", NewStrategy)

def register_search_spaces():
	# save strategy's search space in proper register
	quantflow_factory.QuantFlowFactory.register_search_space(
		"NewStrategy.search_space", NewStrategy.search_space
	)
```

### Add Position Size Policy

To add a position sizing component, same as with strategies, we need to create the component
We need to inherit the basic vol target component and override `position_size_vect` method :

```python
from minimelo.pose_size import BaseSizePolicy
import pandas as pd


class NewVolTargetPolicy(BaseSizePolicy):

	def __init__(
		self,
		annual_vol_target: float,
		trading_capital: float
	):
		super(NewVolTargetPolicy, self).__init__(
			annual_vol_target, trading_capital
		)

	# this is the method we need to override
	# computes number of contracts to buy/sell depending on forecast and risk appetite
	def position_size_vect(self, forecast: pd.Series, lookback: int = 36) -> pd.Series:
		pass
```
Then we register the component to the factory in order to use it with mql.
```python
# find this function in melo_fwk.quantfactory_registry
def register_size_policies():
	# add this line to register your component to be used with mql
	quantflow_factory.QuantFlowFactory.register_size_policy(
		"NewVolTargetPolicy", NewVolTargetPolicy
	)
```

### Add Estimator

Same for estimator as for stategies and size policies. 
Estimators are used to perform various optimization tasks (strategies hyperparameters, forecast weights, portfolio allocation...)
Melo-Fwk implements some estimators already, but if you need to make your own, you need to follow this template
```python
# import necessities

class MyNewEstimator:

	def __init__(
		self,
		products: dict,
		time_period: List[int],
		strategies: List[BaseStrategy] = None,
		forecast_weights: List[int] = None,
		size_policy: BaseSizePolicy = None,
		estimator_params: List[str] = None
	):
		pass # initialize the estimator

	def run(self):
		# every estimator needs to implement a run method
		pass  # usually returns a result passed to a reporting component 
		# check melo_fwk.reporters for example
```
Then register both estimator and associated reporter to the factory `melo_fwk.quantfactory_registry`
```python
# find register_estimator 
# register estimator and reporter
def register_estimator():
	quantflow_factory.QuantFlowFactory.register_estimator("MyNewEstimator", MyNewEstimator)
	quantflow_factory.QuantFlowFactory.register_reporter("MyNewEstimator", MyNewReporter)

```


