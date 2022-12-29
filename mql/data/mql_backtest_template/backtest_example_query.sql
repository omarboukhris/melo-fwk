create BacktestExample
with
    Commodities (Gold, Silver, Palladium, Coffee)
    Fx (EURUSD)
from 2004 to 2008

where strategies are (ewma, ewma)
with strategyConfig (ewma_strat_0, ewma_strat_0)
with weights (0.5, 0.5) and divmult is 0.7

where sizePolicy is VolTargetInertiaPolicy (0.5, 100000)

select BacktestEstimator
export as Backtest1
