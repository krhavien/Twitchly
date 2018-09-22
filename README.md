# Twitchly
Providing efficient automated solutions to Twitch users since 2018.
## Overview
Twitchly is a project started by a team of enthusiastic engineers from UC Berkeley.
Using Twitch API and Data Science techniques, we are looking to answer two primary questions:
- Given a channel, who should the channel partner/collaborate with to gain the most positive growth (defined in increase of viewership/following/subscription)?
- Given a user, which channels can we best recommend to the user?
## Resources
Much of the data we will be leveraging will come directly from [Twitch API](https://dev.twitch.tv/docs/api/reference/).

Follow this [guide](TwitchlyBasicDemo.ipynb) that I wrote up to get familiar with some basic API functionalities.

## Tackling the Problem: V1
For this project, we want to first answer the question:
>>> ```How similar are two channels?```

Once we can answer this comparison question, we can answer our two primary questions stated in the **Overview**.

Let's talk about the second question which has a sub question of:
>>> ``` Should we recommend channel (c) to user (u)? ```

We can start this approach with a simple greedy algorithm:
- Find the set of channels that we could recommend to `u` by looking at all the channels `u` is currently following/subscribed to `u_channels`, see which other users are also following those channels, and then for each of these users, finding who they follow.
  - The output should be a mapping of (`key` -> `user` : `value` -> `followed_channels`)
- We filter through the results by only selecting key-value pairs that have a certain % set match of followed_channels as `u_channels`. (Note we can optimize our filter by actually doing a pre-filter in step 1).
- For each `value` in the key-value pairs, we make a comparison to see how similar each `channel` is with the original `u_channels` and provide it a relevance score.
- We return the top 5 channels with the highest relevance score.
