import requests
import requests
import json
import hmac
import hashlib
import time


class Trader:
	def __init__(
		self,
		api_key,
		api_secret,
		base_url='https://api.binance.com',
		testnet_base_url='https://testnet.binance.com'
	):
		self.api_key = api_key
		self.api_secret = api_secret
		self.base_url = base_url
		self.testnet_base_url = testnet_base_url
		self.backtesting = False

	def execute_trade(self, symbol, side, quantity, price, order_type='LIMIT'):
		if self.backtesting:
			# Creates and validates a new order but
			# does not send it into the matching engine
			# rework the mechanics
			endpoint = '/api/v3/order/test'
			base_url = self.testnet_base_url
		else:
			endpoint = '/api/v3/order'
			base_url = self.base_url
		params = {
			'symbol': symbol,
			'side': side,
			'type': order_type,
			'quantity': quantity,
		}
		if order_type == 'LIMIT':
			params.update({
				'timeInForce': 'GTC',
				'price': price,
			})
		params.update({
			'recvWindow': 5000,
			'timestamp': int(time.time() * 1000)
		})
		query_string = '&'.join([f'{key}={params[key]}' for key in params])
		signature = hmac.new(self.api_secret.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256)
		params['signature'] = signature.hexdigest()
		headers = {
			'X-MBX-APIKEY': self.api_key
		}
		if self.backtesting:
			print(f'[BACKTESTING] {order_type} {side} {quantity} {symbol} at {price}')

		response = requests.post(f'{base_url}{endpoint}', params=params, headers=headers)
		print(response.json())

	def set_backtesting(self, value):
		self.backtesting = value


if __name__ == "__main__":
	# Initialize the trader
	api_key = 'YOUR_API_KEY'
	api_secret = 'YOUR_API_SECRET'
	trader = Trader(api_key, api_secret)

	# Enable backtesting
	trader.set_backtesting(True)

	# Execute a limit buy order for 0.01 BTC at a price of $10,000
	trader.execute_trade('BTCUSDT', 'BUY', 0.01, 10000)
