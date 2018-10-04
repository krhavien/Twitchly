# Twitchly Developer Notes

## 09/27/2018
### Question
Let's recap on what we are first trying to address:
> For a given user `u_input`, recommend channels `rec_ch_list` that `u_input` would be interested in.
### Thoughts
I believe that we can tackle this question in 3 steps:
1. Find the user list `u_list` that are similar to `u_input`.
2. Get the channel set `ch_set` from all the users `u_i` in `u_list`.
3. Rank `ch_set` and return the ordered list  `rec_ch_list`.

#### 1. find_similar_users
- Collect `u_list` that have close distribution with `u_input` (Can be KNN or Least Squares)
  - from database 
  - through `u_input`'s followed channels `followed_ch_list` and checking each channel `ch_i` for followers
  to get sample of users `u_i`.
- Return top % results as set `u_list`.

#### 2. get_channels_from_users
- For each `u_i` in `u_set`, get all followed channels `ch_list`, then store in and return channel set `ch_set`.

#### 3. rank_channels
- TBD

### Tasks
- Create python module called **twitch_client_setup** that authenticates and connects to Twitch API
- Create python module called **find_similar_users** which has following functions:
  - calculating a user's distribution
  - grab user's from the database (may need to index the database by games to optimize querying)
  - grab user's via `u_input`'s followed channels
  - calculate `u_list` by comparing grabbed users with `u_input`
- Create python module called **find_followed_channels** which has following functions:
  - Get followed channels from a given user.
  - get set of followed channels from a list of users.
- Create python module called **rank_channels** which does the following:
  - TBD
- Create main Jupyter Notebook which runs all the modules and exposes an API endpoint for frontend to call.

### ML Model Design Proposals
#### Proposal #1 (Aditya)

**Main Idea**: Unsupervised Gamer Profile Clustering + Algorithmic Profile Matching/Recommendation. 

Use unsupervised learning to come up with a model to classify a particular gamer into a particular gamer profile from a pre-built set of profiles (constructed from info from thousands of users.)
  - How it works:
    - Unsupervised learning relies on patterns intrinsic to the data (no labeling). 
    - Collect lots of data about various streamers and followers (say 10K users across 20 games)
    - Use an unsupervised learning algorithm to create clusters using that info. K-means clustering would be a good start. 
    - Label each record with its assigned cluster (for faster lookup/groupbys later on)
      - Note: if our data is good, we could have up to M different clusters, where M would be the number of user profiles we'd like to cater to.
    - To classify a user, call `model.predict(user)` using their information.
    - Out of all records in the cluster, algorithmically select find the best matching profiles (top 5%) to the current user.
      - Can do this by comparing more advanced statistics of each user (not necessarily the coarser info passed into training the clustering algorithm) 
    - We would then use set differences to figure out which streams to suggest.

  - *Pros:*
    - Don't need to dig through data too much or worry about the various definitions of gamer profiles
    - Can focus on EDA for finding best features, plotting clusters, things like that instead of model-building and parameter tuning. *More demo-friendly.*
    - **We can frontload all the data acquisition.** Only 1 API call to Twitch to get the user's information. All the other data would already have been used to build our model (and available thru pandas at runtime). 
  - *Cons:*
    - Unsupervised learning traditionally has lots of gimmicks, and it will probably take many tries to get the features and data right since we won't have control over what profiles get made. 
    - Might be difficult to convert the data to a format acceptable for clustering (but there are ways of getting around this, particularly through one-hot encoding and vector embedding for text.)
    - **May prevent us from *fully* personalizing the experience.** We must cast each user into a predefined bucket and then do lookups from that bucket. Other users may be cast into the same bucket even if their preferences differ in some way.
      - The part after clustering still allows for user-specific recommendation.
      - However, it may not be as specific as looking at streamers the current user follows and then providing suggestions based on that.
        - As a backup, once the classification + matching happens, we could also provide suggestions from mutual-follow users ("streams followed by users who follow (your favorite streamer)").
        - We could also increase the number of clusters to make initial profile selection more specific. This could be risky due to lack of control over how clustering gets done.
