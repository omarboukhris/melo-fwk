
from melo_fwk.config.melo_config import MeloConfig
from melo_fwk.reporters.md_formatter import MdFormatter
from melo_fwk.plots import TsarPlotter

class BacktestReporter:

	def __init__(self, input_config: MeloConfig):
		"""
		Displays input parameter responsible for the generated results
		Could be report header

		:param input_config:
		:return:
		"""
		# name:
		self.name = input_config.name

		# products:
		self.products_name_list = list(input_config.products_config[0].keys())
		self.begin, self.end = input_config.products_config[1]

		# size policy:
		self.vol_target = input_config.vol_target

		# strategies:
		self.strat_list = [str(x) for x in input_config.strategies_config[0]]
		self.fw = input_config.strategies_config[1]

	def header(self):
		ss = MdFormatter.h1(f"Backtest - {self.name} from {self.begin} to {self.end}")
		ss += MdFormatter.h2("Products:")
		ss += MdFormatter.item_list(self.products_name_list)

		ss += MdFormatter.h2("VolTarget:")
		ss += MdFormatter.item_list(str(self.vol_target).split("\n")[:-1])

		ss += MdFormatter.h2("Strategies:")
		ss += MdFormatter.item_list([f"{w} x {strat}" for w, strat in zip(self.fw, self.strat_list)])

		return ss

	@staticmethod
	def process_results(raw_results: dict):
		"""
		raw_results dict :
			key = product name
			Value = dict :
				key = product_filepath + year
				value = TSAR
		"""
		ss = ""
		for product_name, tsar_dict in raw_results.items():

			assert isinstance(tsar_dict, dict), \
				f"(BacktestReporter) TSAR result {product_name} is not associated to a dict"

			for prod_fn_y, tsar in tsar_dict.items():
				tsar_png = f"assets/{prod_fn_y}.png"
				TsarPlotter.save_tsar_as_png(tsar_png, tsar)

				title = prod_fn_y.replace("_", " ")
				ss += MdFormatter.h2(title)
				ss += MdFormatter.image(title, tsar_png, prod_fn_y)

		return ss
