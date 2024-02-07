import uuid

import azure.batch.models as batchmodels

class MAzureManager:

	def __init__(self):
		self.pool_info = None
		self.batch_client = None

	def create_pool(self):
		pass

	def create_job(self, job_id: str = uuid.uuid4()):
		job = batchmodels.JobAddParameter(id=job_id, pool_info=self.pool_info)
		self.batch_client.job.add(job)

	def submit_task(self):
		pass

