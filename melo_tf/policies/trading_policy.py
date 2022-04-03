

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

	threshold = 2

	def __init__(self):
		super(BaseTradingPolicy, self).__init__()

	def enter_trade_predicat(self, forecast: float):
		self.forecasts.append(forecast)
		return not (-BaseTradingPolicy.threshold < forecast < BaseTradingPolicy.threshold)

	def exit_trade_predicat(self, forecast: float):
		self.forecasts.append(forecast)
		return -BaseTradingPolicy.threshold < forecast < BaseTradingPolicy.threshold

	def turnover_predicat(self, forecast: float):
		turnover = forecast * self.forecasts[-1] < 0
		self.forecasts.append(forecast)
		return turnover



