import ibapi.contract

class ContractFactory:
	@staticmethod
	def create_futures_contract(symbol, expiry, exchange):
		# Create a new contract object
		contract = ibapi.contract.Contract()

		# Set the contract details
		contract.symbol = symbol
		contract.secType = 'FUT'
		contract.expiry = expiry
		contract.exchange = exchange

		return contract

	@staticmethod
	def create_options_contract(symbol, expiry, option_type, strike, exchange):
		# Create a new contract object
		contract = ibapi.contract.Contract()

		# Set the contract details
		contract.symbol = symbol
		contract.secType = 'OPT'
		contract.expiry = expiry
		contract.optionType = option_type
		contract.strike = strike
		contract.exchange = exchange

		return contract

	@staticmethod
	def create_fx_contract(symbol, exchange):
		# Create a new contract object
		contract = ibapi.contract.Contract()

		# Set the contract details
		contract.symbol = symbol
		contract.secType = 'CASH'
		contract.exchange = exchange

		return contract
