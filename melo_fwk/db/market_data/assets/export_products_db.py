from melo_fwk.db.market_data.assets.products_db_mgr import MarketDataDbManager
from melo_fwk.loggers.console_logger import ConsoleLogger
from melo_fwk.loggers.global_logger import GlobalLogger
from melo_fwk.db.market_data import MarketDataLoader


if __name__ == "__main__":
	GlobalLogger.set_loggers([ConsoleLogger])
	products = MarketDataLoader.get_commodities()

	p = MarketDataDbManager(dburl="mongodb://localhost:27017/")
	p.connect("market")

	for product in products:
		p.export_product_to_mongo("co.", product)

	products = MarketDataLoader.get_fx()

	for product in products:
		p.export_product_to_mongo("fx.", product)

	p.close()

