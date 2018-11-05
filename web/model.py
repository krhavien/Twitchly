
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

SAMPLE_FILE_NAME = 'channels_sample_2000.csv'


class KMeansModel:
	""" Creates a K-Means Clustering model that uses unsupervised learning to cluster records in featurized dataframes """

	def __init__(self, n_clusters):
		self.n_clusters = n_clusters
		self.model = KMeans(n_clusters=15, random_state=14)
		self.data = None

	def train(self, input_data=None, assign_clusters=False):
		"""
		Trains model and, optionally, assigns cluster numbers to each of the elements in the data.
		Arguments:
		- input_data: dataframe containing data. Default: None, uses the csv containing sample data in this case
		- assign_clusters: if true, go back into DF and assign clusters in a column called 'pred_cluster'
		"""
		if input_data:
			X = input_data
		else:
			X = pd.read_csv(SAMPLE_FILE_NAME, encoding='ISO-8859-1')
		
		X = self.preprocess(X)
		self.model.fit(X.select_dtypes(include=['int64']))
		
		if assign_clusters:
			X['pred_cluster'] = self.predict(X)
			self.data = X # save locally for future group-by/aggregation

	def predict(self, X):
		"""
		Predicts numerical cluster, some value in range [0 to n_clusters], for each record in X.
		Arguments:
		- X: preprocessed dataframe
		Returns: Predicted cluster
		"""
		X = self.preprocess(X)
		return self.model.predict(X.select_dtypes(include=['int64']))


	def preprocess(self, X):
		if not isinstance(X, pd.DataFrame):
			X = pd.DataFrame([X])
		t = X.drop_duplicates(subset=['id'])
		t = t.dropna(subset=['views', 'follows', 'broadcaster_language', 'followers', 'language', 'id'], how='any')
		t = t[['views', 'broadcaster_language', 'display_name', 'followers', 'game', 'language', 'id', 'follows']]
		t['followers'] = t['followers'].map(int)
		t['views'] = t['views'].map(int)
		t['game_idx'] = t['game'].map({game: num for num, game in enumerate(t['game'].unique())})
		return t

def create_model(n_clusters=10):
	""" External endpoint for creating a model capable of training and predicting clusters. """
	return KMeansModel(n_clusters)


"""
SAMPLE CODE:

import twitchly_db
try:
    db = twitchly_db.Database()
except ValueError:
    db = db
channel_id = '19571641' # ninja's channel id

model = create_model()
model.train(assign_clusters=True)

ninja_pred = model.predict(db.get_user_info(channel_id))
print('Predicted cluster for Ninja: ', ninja_pred)
print('Similar matches')
print(model.data[model.data['pred_cluster']==ninja_pred[0]][['display_name', 'followers']])

OUTPUT (untuned model, trained on sample data):

Predicted cluster for Ninja:  [9]
Similar matches
        display_name  followers
0              Ninja   11884880
73   BeyondTheSummit     716330
136      Starladder1     476067

"""