
from melo_fwk.datastreams.hloc_datastream import HLOCDataStream
from dataclasses import dataclass

@dataclass(frozen=True)
class Product:
	name: str
	block_size: int
	datastream: HLOCDataStream

	def years(self):
		return self.datastream.years

	def get_year(self, year: int):
		assert year in self.years(), f"(AssertionError) Product {self.name} : {year} not in {self.years()}"
		return Product(
			name=self.name,
			block_size=self.block_size,
			datastream=self.datastream.get_data_by_year(year)
		)
