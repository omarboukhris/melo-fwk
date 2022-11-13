create StratOptimExample2
with Commodities (Gold)
from 2004 to 2007

where strategies
	are (ewma)
	with strategyConfig (
	    ewma.search_space
    )

where sizePolicy is VolTargetInertiaPolicy (0.4, 100000)

select StratOptimEstimator<sharpe, 256>
