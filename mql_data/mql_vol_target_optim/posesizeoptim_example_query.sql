create PoseSizeOptimExample
with
    Commodities (Gold, Silver, Palladium, Coffee)
    Commodities (Oat)
from 2004 to 2020

where strategies
	are (ewma)
    with strategyConfig (ewma_strat_0)

where sizePolicy is VolTargetSizePolicy

select VolTargetEstimator <1000000>
