create PoseSizeOptimExample
with
    Commodities (Gold, Silver, Palladium, Coffee)
    Commodities (Oat, Cocoa)
    trade single
from 2004 to 2008

where strategies
	are (ewma, sma)
    with strategyConfig (ewma_strat_0, sma_strat_0)
	and forecastWeights (0.5, 0.5)

where sizePolicy (VolTargetSizePolicy)

select VolTargetEstimator <100000>
