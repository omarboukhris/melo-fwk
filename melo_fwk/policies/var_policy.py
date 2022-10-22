from dataclasses import dataclass

"""
run some MC sims :
	markets shake up
	doomsday scenario
	microcrash event
	short squeeze

Check VaR and adjust size accordingly?
	
"""

@dataclass(frozen=True)
class VaR:
	var: float
