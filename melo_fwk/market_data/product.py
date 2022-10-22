
from melo_fwk.datastreams.hloc_datastream import HLOCDataStream
from dataclasses import dataclass

@dataclass(frozen=True)
class Product:
	name: str
	block_size: int
	datastream: HLOCDataStream

	def years(self):
		return self.datastream.years
