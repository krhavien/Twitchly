
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

SAMPLE_FILE_NAME = 'channels_sample_2000.csv'


class KMeansModel:
	""" Creates a K-Means Clustering model that uses unsupervised learning to cluster records in featurized dataframes """

	def __init__(self, n_clusters=15):
		self.n_clusters = n_clusters
		self.model = KMeans(n_clusters=n_clusters, random_state=14)
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
		self.model.fit(X.select_dtypes(include=['int64','float64']))
		
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
		return self.model.predict(X.select_dtypes(include=['int64','float64']))


	def preprocess(self, X):
		"""
		Converts X to a dataframe object ready for use by the K-Means Model
		- Required columns: ['views', 'broadcaster_language', 'display_name', 'followers', 'game', 'language', 'id', 'follows']
		- Featurizes X to include:
			- game index: a number assigned to a particular game

		Returns: new dataframe object with adjusted columns.
		"""
		if not isinstance(X, pd.DataFrame):
			X = pd.DataFrame([X])
		t = X.drop_duplicates(subset=['id'])
		t = t.dropna(subset=['views', 'follows', 'broadcaster_language', 'followers', 'language', 'id'], how='any')
		t = t[['views', 'broadcaster_language', 'display_name', 'followers', 'game', 'language', 'id', 'follows']]
		t['followers'] = t['followers'].map(int)
		t['views'] = t['views'].map(int)
		t['game_idx'] = t['game'].map({game: num for num, game in enumerate(t['game'].unique())})

		# normalize data using min/max scaling
		scaler = MinMaxScaler()
		t[['followers', 'views']] = scaler.fit_transform(t[['followers', 'views']])
		return t

def create_model(n_clusters=10):
	""" External endpoint for creating a model capable of training and predicting clusters. """
	return KMeansModel(n_clusters)


"""
SAMPLE CODE:
"""
"""
# initialize db
import twitchly_db
try:
    db = twitchly_db.Database()
except ValueError:
    db = db

# ninja's channel id
channel_id = '19571641' 

# create model / predict
model = create_model(n_clusters=10)
model.train(assign_clusters=True)
ninja_pred = model.predict(db.get_user_info(channel_id))

# show results
print('Predicted cluster for Ninja: ', ninja_pred)
print('Similar matches')
print(model.data[model.data['pred_cluster']==ninja_pred[0]][['display_name', 'followers']])
print(model.data.groupby('pred_cluster').count().views)
"""