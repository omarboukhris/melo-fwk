create BacktestExample
with
    Commodities (Gold, Silver, Palladium, Coffee)
    Commodities (Oat, Cocoa)
    trade idx

where strategies
	are (ewma, sma)
	with strategyConfig (ewma_strat_0, sma_strat_0)
	and forecastWeights (0.5, 0.5)

where volTarget
	is (0.5, 100000)
	with sizePolicy (VolTargetSizePolicy)

select backtestEstimator
