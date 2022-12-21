-- AllocOptim will need to be done on whole portfolio instead of subsystem

create portfolio

having (
    cluster1,
    cluster2,
)

with weights (
    0.6, 0.4
)

exec PortfolioVolTarget
-- could also exec allocOptimWeights / VaRReport / ...
-- set it at same level as clustering query
-- also useful for var reporting on portfolio
