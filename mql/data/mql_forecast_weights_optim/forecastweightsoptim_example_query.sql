create ForecastWeightsOptimExample
with
    Commodities (Gold, Silver, Palladium, Coffee)
    Commodities (Oat, Cocoa)
    trade idx
from 2004 to 2008

where strategies
	are (ewma, sma)
	with strategyConfig (ewma_strat_0, sma_strat_0)

select ForecastWeightsEstimator
