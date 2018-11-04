
import pandas as pd
import numpy as np

class KMeansModel:

	def __init__(self, n_clusters):
		self.n_clusters = n_clusters

	def train(self, input_data):
		return

	def preprocess(self, record):
		return

	def predict(self, X):
		return


def create_model(n_clusters=10):
	return KMeansModel(n_clusters)