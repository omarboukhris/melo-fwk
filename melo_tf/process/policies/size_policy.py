
from risk_policy import *

class ISizePolicy:

	def __init__(self, datastream, risk_policy: IRiskPolicy):
		self.datastream = datastream
		self.risk_policy = risk_policy

