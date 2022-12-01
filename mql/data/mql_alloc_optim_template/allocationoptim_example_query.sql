-- AllocOptim will need to be done on whole portfolio instead of subsystem

create portfolio

having (
    cluster1,
    cluster2,
)

exec PortfolioVolTarget
-- could also exec allocOptimWeights
-- set it at same level as clustering query
-- also useful for var reporting on portfolio
