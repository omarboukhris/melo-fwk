from dataclasses import dataclass

from melo_fwk.estimators_clusters.base_cluster_estimator import BaseClusterEstimator


@dataclass(frozen=True)
class PFVaREstimator(BaseClusterEstimator):

	def run(self):
		pass