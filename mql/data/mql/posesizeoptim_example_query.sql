create PoseSizeOptimExample
with
    Commodities (Gold, Silver, Palladium, Coffee)
    Commodities (Oat, Cocoa)
    trade idx
from 2004 to 2008

where strategies
	are (ewma, sma)
	with strategyConfig (ewmaConfig, smaConfig)
	and forecastWeights (0.5, 0.5)

where volTarget
	is (*, 100000)
	with sizePolicy (VolTargetSizePolicy)

select poseSizeOptimEstimator
