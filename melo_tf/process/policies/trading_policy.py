

class ITradingPolicy:

	def __init__(self):
		self.forecasts = []

	def enter_trade_predicat(self, forecast: float):
		self.forecasts.append(forecast)

	def exit_trade_predicat(self, forecast: float):
		self.forecasts.append(forecast)

	def turnover_predicat(self, forecast: float):
		self.forecasts.append(forecast)


class BaseTradingPolicy(ITradingPolicy):

	THRESHOLD = 1e-3

	def __init__(self, threshold=THRESHOLD):
		super(BaseTradingPolicy, self).__init__()
		self.threshold = threshold

	def enter_trade_predicat(self, forecast: float):
		self.forecasts.append(forecast)
		return not (-self.threshold < forecast < self.threshold)

	def exit_trade_predicat(self, forecast: float):
		return not self.enter_trade_predicat(forecast)

	def turnover_predicat(self, forecast: float):
		self.forecasts.append(forecast)
		turnover = forecast * self.forecasts[-1] < 0
		return turnover



