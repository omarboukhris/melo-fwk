

class ITradingPolicy:

	def __init__(self):
		self.forecasts = []

	def enter_trade_predicat(self, forecast: float):
		self.forecasts.append(forecast)

	def exit_trade_predicat(self, forecast: float):
		self.forecasts.append(forecast)

class BaseTradingPolicy(ITradingPolicy):

	def __init__(self):
		super(BaseTradingPolicy, self).__init__()

	def enter_trade_predicat(self, forecast: float):
		self.forecasts.append(forecast)
		return forecast != 0 and forecast is not None

	def exit_trade_predicat(self, forecast: float):
		self.forecasts.append(forecast)
		return -.1 < forecast < .1




