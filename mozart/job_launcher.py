from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Pool

import pandas as pd


class JobLauncher:

	def __init__(self, func: callable, pool_size: int, use_thread: bool = False):
		self.job = func
		self.pool = Pool(processes=pool_size) if not use_thread else ThreadPool(processes=pool_size)
		self.res_list = {}
		self.status_df = None
		self.proc = None
		self.done = set({})
		self.running = set({})

	def setup(self, proc):
		self.proc = set(proc)
		self.done = set({})

	def update(self):
		done = set(row["job"] for _, row in self.status_df.iterrows() if row["status"])
		self.done.update(done)

	def process_running(self):
		return not self.status()["status"].any() and self.is_not_done()

	def is_not_done(self):
		return self.done != self.proc

	def submit(self, candidates: dict):
		self.res_list.update({c: self.pool.apply_async(self.job, (*params,)) for c, params in candidates.items()})
		self.running.update(list(candidates.keys()))

	def status(self):
		self.status_df = pd.DataFrame([
			(k, r.successful()) for k, r in self.res_list.items()
			if r.ready() and k not in self.done
		], columns=["job", "status"])
		return self.status_df

	def submitted_jobs(self):
		return self.running.union(self.done)

