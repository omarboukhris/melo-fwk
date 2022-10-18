
from melo_fwk.market_data.utils.hloc_datastream import HLOCDataStream
from dataclasses import dataclass

@dataclass(frozen=True)
class Product:
	name: str
	datastream: HLOCDataStream
