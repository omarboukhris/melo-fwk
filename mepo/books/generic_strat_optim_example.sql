create StratOptimExample2
with Commodities (Gold)
from 2004 to 2008

where strategies are ($ewma)

where sizePolicy is VolTargetSizePolicy (0.4, 100000)
