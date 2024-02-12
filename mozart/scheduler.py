import random
from functools import reduce
from time import sleep

import numpy as np
import pandas as pd

from mepo import books
from mozart.job_launcher import JobLauncher
from mql.melo_machina import MeloMachina
from mutils.generic_config_loader import GenericConfigLoader
from mutils.loggers.console_logger import ConsoleLogger
from mutils.loggers.global_logger import GlobalLogger


class TestHelper:
	@staticmethod
	def test_param_map(candidates):
		return {c: (c, random.randint(3, 10),) for c in candidates}

	@staticmethod
	def process_factory(c, x):
		print(f"executing {c} for {x} seconds")
		sleep(x)
		print(f"end {c}")
		return x


class MeloProcessHelper:
	process: str
	estim_config: str
	export_path: str
	# loggers_list: list
	process_config: list

	# add setup method

	@staticmethod
	def melo_param_factory(book_name):
		return (
			book_name,
			MeloProcessHelper.process,
			MeloProcessHelper.estim_config,
			MeloProcessHelper.export_path,
			[ConsoleLogger],
			MeloProcessHelper.process_config
		)

	@staticmethod
	def melo_process(
		book_name: str,
		process: str,
		estim_config: str,
		export_path: str,
		loggers_list: list,
		process_config: list
	):
		GenericConfigLoader.setup(process_config)
		GlobalLogger.set_loggers(loggers_list)

		mm = MeloMachina()

		book_path = books.auto_books.get(book_name)
		mm.run(
			export_path=export_path,
			book_path=book_path,
			process=process,
			config=estim_config,
		)
		# take export out of melomachina


class JobScheduler:

	def __init__(self, dep_map: dict, job_launcher: JobLauncher):
		self.job_launcher = job_launcher
		self.dep_map = dep_map
		self.sanity_check()
		self.proc = list(self.dep_map.keys())
		nproc = len(self.proc)
		self.dep_mat = pd.DataFrame(
			data=np.zeros(shape=(nproc, nproc)),
			index=self.proc,
			columns=self.proc,
		)
		for p in self.proc:
			self.dep_mat.loc[p, self.dep_map[p]] = 1

	def sanity_check(self):
		nodes_k = set(self.dep_map.keys())
		nodes_v = set(reduce(lambda a, b: a+b, self.dep_map.values(), []))
		missing = nodes_v - nodes_k
		assert len(missing) == 0, \
			f"(Scheduler) Missing nodes in process dependency map {missing}"

	def start(self, param_setup_factory: callable):
		self.job_launcher.setup(self.proc)
		while self.job_launcher.is_not_done():
			excl = self.job_launcher.submitted_jobs()
			candidates = self.get_next_jobs() - excl
			candidates_map = param_setup_factory(candidates)
			self.job_launcher.submit(candidates_map)
			while self.job_launcher.process_running():
				sleep(1)  # get this from config, refresh rate
			# update/aggregate shared memory space
			self.update_dependency_mat(self.job_launcher.status_df)
			self.job_launcher.update()

	def update_dependency_mat(self, status_df: pd.DataFrame):
		for _, row in status_df.iterrows():
			job, status = row["job"], row["status"]
			self.dep_mat[job] = 0 if status else 1

	def get_next_jobs(self):
		dep_mat = self.dep_mat.copy()
		dep_mat["SUM_DEP"] = dep_mat.sum(axis=1)
		candidates = set(dep_mat[dep_mat["SUM_DEP"] == 0].index)
		return candidates


if __name__ == "__main__":
	d = {
		"t1": [],
		"t2": ["t1"],
		"t3": ["t1"],
		"t4": ["t3"],
		"t5": ["t2", "t4"],
		"t6": ["t2", "t3"],
	}

	j = JobLauncher(func=TestHelper.process_factory, pool_size=2)
	s = JobScheduler(d, j)
	s.start(TestHelper.test_param_map)


