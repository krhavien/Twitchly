# Twitchly
Providing efficient automated solutions to content creators since 2018.
## Overview
Twitchly is a project started by a team of enthusiastic engineers from UC Berkeley.
Using Twitch API and machine learning techniques, we are looking to answer two primary questions:
- Given a set of streamers and a main streamer, who should the main streamer partner/collaborate with in the set to gain the most positive growth (defined in increase of viewership/following/subscription)?
- Given a user and a set of streamers, which streamers from the set can we best recommend to the user based on that user's historical data?
## Resources
Much of the data we will be leveraging will come directly from [Twitch API](https://dev.twitch.tv/docs/api/reference/).
We are primarly interested in (but not limited to) data such as:
- a channel's total `view count`
- a channel's `views` per video
- the type of `games` the channel streams
- a channel's live stream `metadata`
- a channel's set of `followers`
- a user's set of `followed` channels
