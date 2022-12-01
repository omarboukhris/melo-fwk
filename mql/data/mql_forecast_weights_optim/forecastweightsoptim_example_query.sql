
create ForecastWeightsOptimExample
with
    Commodities (Gold, Silver, Palladium, Coffee)
    Commodities (Oat)
from 2004 to 2008

where strategies
	are (ewma, ewma)
	with strategyConfig (ewma_strat_0, ewma_strat_1)

select ForecastWeightsEstimator
