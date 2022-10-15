
import melo_fwk.datastreams.hloc_datastream as ds
from dataclasses import dataclass

@dataclass(frozen=True)
class Product:
	filepath: str
	datastream: ds.HLOCDataStream
