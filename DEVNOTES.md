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
