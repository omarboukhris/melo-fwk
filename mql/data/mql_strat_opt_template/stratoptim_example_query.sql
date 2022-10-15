create StratOptimExample
with
    Commodities (Gold, Silver, Palladium, Coffee)
    Commodities (Oat, Cocoa)
    trade idx
from 2004 to 2008

where strategies
	are (ewma, sma)
	with strategyConfig (
	    ewma.search_space,
	    sma.search_space
    )

select StratOptimEstimator
