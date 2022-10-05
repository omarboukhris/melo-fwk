create ForecastWeightsOptimExample
with
    Commodities (Gold, Silver, Palladium, Coffee)
    Commodities (Oat, Cocoa)
    trade idx

where strategies
	are (ewma, sma)
	with strategyConfig (
	    ewmaConfig.search_space,
	    smaConfig.search_space)
	and forecastWeights (*)

select ForecastWeightsOptim