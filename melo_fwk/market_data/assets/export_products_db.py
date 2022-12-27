from melo_fwk.db_mgr.products_db_mgr import MarketDataDbManager
from melo_fwk.loggers.console_logger import ConsoleLogger
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.market_data import MarketDataLoader


if __name__ == "__main__":
	GlobalLogger.set_loggers([ConsoleLogger])
	products = MarketDataLoader.get_commodities()

	p = MarketDataDbManager()
	p.connect("Commodity")

	for product in products:
		p.export_product_to_mongo(product)

	products = MarketDataLoader.get_fx()
	p.connect("Fx")

	for product in products:
		p.export_product_to_mongo(product)

	p.close()


