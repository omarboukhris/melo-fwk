from melo_tf.mql_parser import quantflow_factory

from process import trading_system

from rules import ewma_rule, sma_rule

from process.policies import vol_target_policy


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
