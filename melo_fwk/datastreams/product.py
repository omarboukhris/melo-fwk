
from melo_fwk.datastreams.hloc_datastream import HLOCDataStream
from dataclasses import dataclass

@dataclass(frozen=True)
class Product:
	filepath: str
	datastream: HLOCDataStream
