

class ITradingPolicy:

	def __init__(self):
		pass

	def enter_trade_predicat(self, forecast: float):
		pass

	def exit_trade_predicat(self, forecast: float):
		pass

class BaseTradingPolicy(ITradingPolicy):

	THRESHOLD = 1e-3

	def __init__(self, threshold=THRESHOLD):
		super(BaseTradingPolicy, self).__init__()
		self.threshold = threshold

	def enter_trade_predicat(self, forecast: float):
		return not (-self.threshold < forecast < self.threshold)

	def exit_trade_predicat(self, forecast: float):
		return not self.enter_trade_predicat(forecast)



