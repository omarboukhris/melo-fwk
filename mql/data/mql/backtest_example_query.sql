with Commodities (Gold, Silver, Paladium)
trade underlying
where strategies
	are (ewma, sma)
	with strategyConfig (ewmaConfig, smaConfig)
	and forecastWeights (0.5, 0.5)
where volTarget
	is (0.5, 100000)
	with sizePolicy (s)
select backtestEstimator
