
import yaml

def read_strat_config_point(config_point_fn: str):
	config_points_registry = {}
	try:
		with open(config_point_fn, "r") as stream:
			content = yaml.safe_load(stream)
			config_points_registry.update(content)
	except yaml.YAMLError as exc:
		print(f"(YAMLError) {exc}")
	except Exception as e:
		print(f"(Exception) yaml_io.read_strat_config_point : {e}")
	finally:
		return config_points_registry

def write_strat_config_point(config_points_registry: dict, config_point_fn: str):
	try:
		with open(config_point_fn, "w") as stream:
			for k, v in config_points_registry.items():
				yaml.dump({k: v}, stream)
	except yaml.YAMLError as exc:
		print(f"(YAMLError) {exc}")
	except Exception as e:
		print(f"(Exception) {e}")
	finally:
		return config_points_registry


