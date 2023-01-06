import ibapi.order


class IBKROrderFactory:
	@staticmethod
	def create_market_order(action, quantity):
		# Create a new order object
		order = ibapi.order.Order()

		# Set the order type and quantity
		order.orderType = 'MKT'
		order.totalQuantity = quantity
		order.action = action

		return order

	@staticmethod
	def create_limit_order(action, quantity, limit_price):
		# Create a new order object
		order = ibapi.order.Order()

		# Set the order type, quantity, and limit price
		order.orderType = 'LMT'
		order.totalQuantity = quantity
		order.lmtPrice = limit_price
		order.action = action

		return order
