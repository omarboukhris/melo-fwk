import random
from functools import reduce
from multiprocessing import Pool
from time import sleep
from typing import List, Set

import numpy as np
import pandas as pd

def factory(c):
	x = random.randint(3, 10)
	print(f"executing {c} for {x}")
	sleep(x)
	print(f"end {c}")
	return x

class JobLauncher:

	def __init__(self, pool_size: int):
		self.pool = Pool(processes=pool_size)
		self.res_list = {}

	def submit(self, candidates: set):
		self.res_list.update({c: self.pool.apply_async(factory, (c,)) for c in candidates})

	def is_done(self, done: Set[str]):
		# print({k: r.successful() for k, r in self.res_list.items() if r.ready()})
		return any(k for k, r in self.res_list.items() if r.ready() and r.successful() and k not in done)

class Scheduler:

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

	def start(self):
		done, proc = set({}), set(self.proc)
		candidates = self._get_next_jobs(done)
		self.job_launcher.submit(candidates)
		while done != proc:
			while not self.job_launcher.is_done(done) and done != proc:
				sleep(1)  # get this from config, refresh rate
			for c in candidates:
				self.dep_mat[c] = 0
			done.update(candidates)
			candidates = self._get_next_jobs(done)
			self.job_launcher.submit(candidates)
		pass

	def _get_next_jobs(self, done_proc: set):
		dep_mat = self.dep_mat.copy()
		dep_mat["SUM_DEP"] = dep_mat.sum(axis=1)
		candidates = set(dep_mat[dep_mat["SUM_DEP"] == 0].index) - done_proc
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

	j = JobLauncher(pool_size=2)
	s = Scheduler(d, j)
	s.start()



