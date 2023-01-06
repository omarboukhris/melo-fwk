import time

import ibapi.order
from ibapi.client import EClient
from ibapi.common import OrderId
from ibapi.contract import Contract
from ibapi.wrapper import EWrapper


class TradeOrderExecutor(EClient, EWrapper):
	def __init__(self, host, port, client_id):
		EWrapper.__init__(self)
		EClient.__init__(self, wrapper=self)

		self.position_received = False
		self.current_position = None
		self.host = host
		self.port = port
		self.client_id = client_id

		# Connect to the API
		self.connect(host, port, client_id)

		# Initialize variables to store order information
		self.order_id = 0
		self.is_order_complete = False

	def place_order(self, contract, order):
		# Send the order to the API
		self.placeOrder(self.reqIds(self.order_id), contract, order)

		# should maybe log some stuff

		# Set the order ID and reset the order complete flag
		self.order_id = self.reqIds(self.order_id)
		self.is_order_complete = False

	def cancel_order(self):
		# Cancel the order
		self.cancelOrder(self.order_id)

	def upade_position_size(self, contract, target_size):
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
			orderId, status, filled, remaining,avgFillPrice, permId, parentId, lastFillPrice, clientId, whyHeld, mktCapPrice)

		# Check if the order is complete
		if status == 'Filled':
			self.is_order_complete = True

	def reqPositions(self):
		self.position_received = False
		super().reqPositions()
