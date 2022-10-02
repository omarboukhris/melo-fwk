from mql import quantflow_factory

from melo_tf.datastreams.commodities import CommodityDataLoader

from melo_tf.process import trading_system

from melo_tf.rules import ewma_rule, sma_rule

from melo_tf.process.policies import vol_target_policy


quantflow_factory.QuantFlowFactory.register_workflow("backtest", trading_system.TradingSystem)
"""
Note: Always roll out of sample (param = lookback)

Estimators : 
	doesn't have to fit(), just implement Estimator.score()
	then pass to BayesSearchCv to optimize parameters/get heatmap

** Select/Map Asset Universe Estimator
n products
select asset universe :
	- strategies : default => buy and hold, const forecast
	- size : default => const size
	- forecast weights : default => equal
	- result :
		cov_mat
		vol by asset
		sliding cointeg heatmap

** Single Strategy Estimator
1-n products, 1 strategy
optimize strategy:
	- size : default => const size
	- result :
		cov_mat returns for each strategy configuration
		sharpe or pnl for each set of params
		drawdown
	note : loose filter, don't need to hyperoptimize returns now, select kinda good strategies

** Forecast Weigths Estimator
1 product
optimize forecast weights:
	- strategies : default => buy and hold, const forecast
	- size : default => const size
	- result :
		forecast weights : => result (sharpe or pnl for each set of weights)
		ordered optimal weights
		drawdown
	Note : average roll out of sample pseudo-optimal weights for observation configuration (backtest)

** Vol Target Estimator
1 product
optimize vol target :
	- strategies : default => buy and hold, const forecast
	- forecast weights : default => equal
	- result :
		vol target : => result (sharpe or pnl for each vol)
		plot : sharpe or pnl = trade_asset(size_policy(vol_target)) 
		drawdown

** Portfolio Estimator ( = Map Universe Estimator)
n products
build portfolio :
	- strategies : default => buy and hold, const forecast
	- size : default => const size
	- forecast weights : default => equal
	- result :
		asset weights : => result (sharpe or pnl for each set of weights)
		ordered optimal wights
		cov_mat returns by asset for optimal weights

Live trading & backtest :
	- wkflow 1 result : universe of traded assets 
	- wkflow 2 result : {forecast weights}_n for each ({strategies}_n, traded asset)
	- wkflow 3 result : vol target for each ({forecast wigths, strategies}_n, traded asset)
	- wkflow 4 result : {asset wigths}_n for ({forecast_weights, strategies}_m, traded asset)_n
"""
quantflow_factory.QuantFlowFactory.register_strategy("ewmacross", ewma_rule.EWMATradingRule)
quantflow_factory.QuantFlowFactory.register_strategy("smacross", sma_rule.SMATradingRule)


quantflow_factory.QuantFlowFactory.register_size_policy("voltargetsizepolicy", vol_target_policy.VolTargetSizePolicy)
quantflow_factory.QuantFlowFactory.register_size_policy("constpolicy", vol_target_policy.ConstSizePolicy)

# =============================================================
# Products Factory Registration
# =============================================================
# Commodities
# -------------------------------------------------------------
# oil
quantflow_factory.QuantFlowFactory.register_product("Commodities.BrentCrudeOil", CommodityDataLoader.BrentCrudeOil)
quantflow_factory.QuantFlowFactory.register_product("Commodities.CrudeOil", CommodityDataLoader.CrudeOil)
quantflow_factory.QuantFlowFactory.register_product("Commodities.HeatingOil", CommodityDataLoader.HeatingOil)
quantflow_factory.QuantFlowFactory.register_product("Commodities.NaturalGas", CommodityDataLoader.NaturalGas)
quantflow_factory.QuantFlowFactory.register_product("Commodities.RBOBGasoline", CommodityDataLoader.RBOBGasoline)

# agricultural
# plants
quantflow_factory.QuantFlowFactory.register_product("Commodities.Cocoa", CommodityDataLoader.Cocoa)
quantflow_factory.QuantFlowFactory.register_product("Commodities.Coffee", CommodityDataLoader.Coffee)
quantflow_factory.QuantFlowFactory.register_product("Commodities.Corn", CommodityDataLoader.Corn)
quantflow_factory.QuantFlowFactory.register_product("Commodities.Cotton", CommodityDataLoader.Cotton)
quantflow_factory.QuantFlowFactory.register_product("Commodities.Soybean", CommodityDataLoader.Soybean)
quantflow_factory.QuantFlowFactory.register_product("Commodities.SoybeanMeal", CommodityDataLoader.SoybeanMeal)
quantflow_factory.QuantFlowFactory.register_product("Commodities.SoybeanOil", CommodityDataLoader.SoybeanOil)
quantflow_factory.QuantFlowFactory.register_product("Commodities.Sugar", CommodityDataLoader.Sugar)
quantflow_factory.QuantFlowFactory.register_product("Commodities.Wheat", CommodityDataLoader.Wheat)

# animals
quantflow_factory.QuantFlowFactory.register_product("Commodities.FeederCattla", CommodityDataLoader.FeederCattla)
quantflow_factory.QuantFlowFactory.register_product("Commodities.LiveCattle", CommodityDataLoader.LiveCattle)

# metals
quantflow_factory.QuantFlowFactory.register_product("Commodities.Copper", CommodityDataLoader.Copper)
quantflow_factory.QuantFlowFactory.register_product("Commodities.Gold", CommodityDataLoader.Gold)
quantflow_factory.QuantFlowFactory.register_product("Commodities.Palladium", CommodityDataLoader.Palladium)
quantflow_factory.QuantFlowFactory.register_product("Commodities.Platinum", CommodityDataLoader.Platinum)
quantflow_factory.QuantFlowFactory.register_product("Commodities.Silver", CommodityDataLoader.Silver)

# unclassified
quantflow_factory.QuantFlowFactory.register_product("Commodities.LeanHogs", CommodityDataLoader.LeanHogs)
quantflow_factory.QuantFlowFactory.register_product("Commodities.Lumber", CommodityDataLoader.Lumber)
quantflow_factory.QuantFlowFactory.register_product("Commodities.Oat", CommodityDataLoader.Oat)

# =============================================================
