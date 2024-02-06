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
		self.status_df = None
		self.proc = None
		self.done = set({})
		self.running = set({})

	def setup(self, proc):
		self.proc = set(proc)
		self.done = set({})

	def update(self, done: Set[str]):
		self.done.update(done)

	def process_running(self):
		return not self.status()["status"].any() and self.is_not_done()

	def is_not_done(self):
		return self.done != self.proc

	def submit(self, candidates: set):
		self.res_list.update({c: self.pool.apply_async(factory, (c,)) for c in candidates})
		self.running.update(candidates)

	def status(self):
		self.status_df = pd.DataFrame([
			(k, r.successful()) for k, r in self.res_list.items()
			if r.ready() and k not in self.done
		], columns=["job", "status"])
		return self.status_df

	def submitted_jobs(self):
		return self.running.union(self.done)


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

	def start(self):
		self.job_launcher.setup(self.proc)
		while self.job_launcher.is_not_done():
			candidates = self._get_next_jobs()
			self.job_launcher.submit(candidates)
			while self.job_launcher.process_running():
				sleep(1)  # get this from config, refresh rate
			done_proc = self.update_dependency_mat(self.job_launcher.status_df)
			# update/aggregate shared memory space
			self.job_launcher.update(done_proc)

	def update_dependency_mat(self, status_df: pd.DataFrame):
		out = []
		for _, row in status_df.iterrows():
			job, status = row["job"], row["status"]
			self.dep_mat[job] = 0 if status else 1
			if status:
				out.append(job)
		return set(out)

	def _get_next_jobs(self):
		dep_mat = self.dep_mat.copy()
		dep_mat["SUM_DEP"] = dep_mat.sum(axis=1)
		candidates = set(dep_mat[dep_mat["SUM_DEP"] == 0].index) - self.job_launcher.submitted_jobs()
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
	s = JobScheduler(d, j)
	s.start()



