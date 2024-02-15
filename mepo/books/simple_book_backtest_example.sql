create BacktestExample
with
    Commodities (Gold, Silver, Palladium, Coffee)
    Fx (EURUSD)
from 2008 to 2009

where strategies are (ewma_strat_0, ewma_strat_0)
with weights (0.5, 0.5) and divmult is 0.7

where sizePolicy is VolTargetInertiaPolicy (0.5, 100000)

