
import scipy.cluster.hierarchy as sch
import pandas as pd
import numpy as np
import random

from typing import List

class ClusterUtils:

	@staticmethod
	def build_corr_hist(correlations: List[pd.DataFrame]):
		corr_hist = {}
		columns = correlations[0].columns
		for i in range(len(columns)):
			for j in range(i + 1, len(columns)):
				si, sj = columns[i], columns[j]
				corr_hist[f"{si}:{sj}"] = [corr[si][sj] for corr in correlations]
		return corr_hist

	@staticmethod
	def get_corr_sample(results, sampling_ratio: float):
		max_len = pd.Series([len(v) for v in results.values()]).min()
		max_samples = int(max_len * sampling_ratio)
		correlations = []
		avg_corr = 0
		for i in random.sample(range(max_len), max_samples):
			corr_mat = pd.DataFrame({
				prod_name: result[i].account_series
				for prod_name, result in results.items()
			}).corr()
			correlations.append(corr_mat)
			avg_corr += corr_mat
		avg_corr /= len(correlations)
		return avg_corr, correlations


	@staticmethod
	def cluster_products(avg_corr):
		# https://github.com/TheLoneNut/CorrelationMatrixClustering/blob/master/CorrelationMatrixClustering.ipynb
		df = pd.DataFrame(avg_corr)
		X = df.corr().values
		d = sch.distance.pdist(X)
		L = sch.linkage(d, method='complete')
		ind = sch.fcluster(L, 0.5 * d.max(initial=0), 'distance')
		columns = [df.columns.tolist()[i] for i in list((np.argsort(ind)))]
		avg_corr = df.reindex(columns, axis=1)
		return avg_corr
