
from dataclasses import dataclass

"""
{'QuantQuery': [{
	'PositionSizing': [{
		'SizePolicy': ['s'], 
		'VolTargetCouple': ['0.5 , 100000 ']}], 
	'ProcessDef': [{'Estimator': ['backtestEstimator']}], 
	'ProductsDef': [{
		'ProductsDefList': [{
			'ProductsList': ['Gold , Silver , Paladium '], 
			'productType': ['Commodities']}], 
		'instrument': ['underlying']}], 
	'StrategiesDef': [{
		'StrategyConfigList': ['ewmaConfig , smaConfig '], 
		'StrategyList': ['ewma , sma '], 
		'forecastWeightsList': ['0.5 , 0.5 ']}]}]}
"""

"""
process dataclass element after init somehow, sanitize config dict, check how to init dataclass manually
somewhere (an intermediate static component) we should pass quantcomponents factory as a parameter to get registered 
components relative to the parsed config and build workflow.
Call to mql parser / config structuring should be done outside at the root folder of the project 
"""

@dataclass(frozen=True)
class ProductConfig:
	productList: list
	productType: str
	instrument: str


@dataclass(frozen=True)
class StrategyConfig:
	strategyList: list
	strategyConfigList: list
	forecastWeightsList: list


@dataclass(frozen=True)
class PositionSizeConfig:
	sizePolicy: str
	volTargetCouple: tuple  # or dict


@dataclass(frozen=True)
class MqlWorkFlowConfig:
	estimator: str
	product: ProductConfig
	strategy: StrategyConfig
	positionPolicy: PositionSizeConfig

