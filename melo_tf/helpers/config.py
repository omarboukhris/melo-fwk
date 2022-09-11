
import yaml

from dataclasses import dataclass
from typing import List

@dataclass(frozen=True)
class WorkflowConfig:
	process: str
	type: str
	product: dict
	strategy: List[dict]
	forecast_weight: List[float]
	vol_target: dict
	size_policy: str
	# output: List[str]

	@staticmethod
	def parse_cfg(filename: str):
		with open(filename, "r") as stream:
			data = None
			try:
				data = yaml.safe_load(stream)
			except yaml.YAMLError as exc:
				print(exc)
				exit(-1)
		wkf_cfg = WorkflowConfig._sanitize_data_keys(data)
		return WorkflowConfig(**wkf_cfg)

	@staticmethod
	def _sanitize_data_keys(data):
		if type(data) == list:
			out = []
			for elm in data:
				out.append(WorkflowConfig._sanitize_data_keys(elm))
			return out
		elif type(data) == dict:
			out = {}
			for k, v in data.items():
				new_key = k.replace("-", "_") if "-" in k else k
				out[new_key] = WorkflowConfig._sanitize_data_keys(v)
			return out
		else:
			return data


if __name__ == "__main__":
	parsedCfg = WorkflowConfig.parse_cfg("../data/ConfigPoints/mvpWorkflow.yaml")
	print(parsedCfg)
