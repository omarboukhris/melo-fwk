import time

import ibapi.order
from ibapi.client import EClient
from ibapi.common import OrderId
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper

class TradeOrderExecutor(EClient, EWrapper):
	"""
	This class is used to execute trades through the Interactive Brokers API. It is a subclass of EClient and EWrapper,
	and therefore it has access to the functions and variables provided by these classes.
	"""

	def __init__(self, host: str, port: int, client_id: int):
		"""
		Constructor for the TradeOrderExecutor class.

		Parameters:
		host (str): The hostname for the Interactive Brokers API.
		port (int): The port number for the Interactive Brokers API.
		client_id (int): The client ID to use when connecting to the Interactive Brokers API.
		"""
		# Call the constructors for the parent classes
		EWrapper.__init__(self)
		EClient.__init__(self, wrapper=self)

		# Initialize variables to store order information
		self.position_received = False
		self.current_position = None
		self.host = host
		self.port = port
		self.client_id = client_id
		self.order_id = 0
		self.is_order_complete = False

		# Connect to the API
		self.connect(host, port, client_id)

	def place_order(self, contract: Contract, order: ibapi.order.Order):
		"""
		This method is used to place an order through the Interactive Brokers API.

		Parameters:
		contract (Contract): The contract details for the order.
		order (ibapi.order.Order): The order details.
		"""
		# Send the order to the API
		self.order_id = self.reqIds(self.order_id)
		self.placeOrder(self.order_id, contract, order)

		# should maybe log some stuff

		# reset the order complete flag
		self.is_order_complete = False

	def cancel_order(self):
		"""
		Cancels the order placed through the API.
		"""
		self.cancelOrder(self.order_id)

	def upade_position_size(self, contract, target_size):
		"""Updates the position size of the given contract to the target size.
		If the current position size is greater than the target size,
		sells a portion of the position to reduce the size to the target size.
		If the current position size is less than the target size,
		buys a portion of the contract to increase the size to the target size.

		:param contract: The contract for which to update the position size.
		:param target_size: The target position size.
		"""
		# Request the current position
		self.reqPositions()

		# Wait for the position response
		while not self.position_received:
			time.sleep(1)

		# Calculate the difference between the current size and the target size
		size_difference = self.current_position - target_size

		# Check if the position needs to be reduced
		if size_difference != 0:
			# Create an order to sell a portion of the position
			order = ibapi.order.Order()
			order.orderType = 'MKT'
			order.totalQuantity = size_difference
			order.action = 'SELL' if size_difference > 0 else "BUY"

			# Send the order to the API
			self.place_order(contract, order)

	def position(self, account: str, contract: Contract, position: float, avgCost: float):
		super().position(account, contract, position, avgCost)
		# Store the position size
		self.current_position = position
		self.position_received = True

	def orderStatus(
		self, orderId: OrderId, status: str, filled: float,
		remaining: float, avgFillPrice: float, permId: int,
		parentId: int, lastFillPrice: float, clientId: int,
		whyHeld: str, mktCapPrice: float):

		super().orderStatus(
			orderId, status, filled, remaining, avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)

		# Check if the order is complete
		if status == 'Filled':
			self.is_order_complete = True

	def reqPositions(self):
		self.position_received = False
		super().reqPositions()
