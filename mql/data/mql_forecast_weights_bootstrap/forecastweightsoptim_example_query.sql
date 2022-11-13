
create ForecastWeightsOptimExample
with
    Commodities (Gold, Silver, Palladium, Coffee)
    Commodities (Oat, Cocoa)
from 2004 to 2008

where strategies
	are (ewma, ewma, sma)
	with strategyConfig (ewma_strat_0, ewma_strat_1, sma_strat_0)

select ForecastWeightsEstimator
