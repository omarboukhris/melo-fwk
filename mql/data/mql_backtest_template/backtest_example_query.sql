create BacktestExample
with
    Commodities (Gold, Silver, Palladium, Coffee)
    Fx (EURUSD)
    trade single

from 2004 to 2008

where strategies are (ewma)
with
    strategyConfig (ewma_strat_0)

where sizePolicy is VolTargetInertiaPolicy (0.5, 100000)

select BacktestEstimator
