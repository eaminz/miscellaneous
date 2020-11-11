#!/usr/bin/env python3

import urllib.request, json

with urllib.request.urlopen(
    "https://static01.nyt.com/elections-assets/2020/data/api/2020-11-03/race-page/pennsylvania/president.json"
) as url:
    raw_data = json.loads(url.read().decode())
    time_series = raw_data["data"]["races"][0]["timeseries"]
    biden_prev_votes = 0
    trump_prev_votes = 0
    biden_vote_decrease_total = 0
    trump_vote_decrease_total = 0
    biden_vote_decrease_times = 0
    trump_vote_decrease_times = 0
    for time_point in time_series:
        total_votes = time_point["votes"]
        biden_cur_votes = total_votes * time_point["vote_shares"]["bidenj"]
        trump_cur_votes = total_votes * time_point["vote_shares"]["trumpd"]
        if biden_prev_votes > biden_cur_votes:
            biden_vote_decrease_total += biden_prev_votes - biden_cur_votes
            biden_vote_decrease_times += 1
        if trump_prev_votes > trump_cur_votes:
            trump_vote_decrease_total += trump_prev_votes - trump_cur_votes
            trump_vote_decrease_times += 1
        biden_prev_votes = biden_cur_votes
        trump_prev_votes = trump_cur_votes
    print(
        "biden_vote_decrease_total=%d\nbiden_vote_decrease_times=%d\ntrump_vote_decrease_total=%d\ntrump_vote_decrease_times=%d"
        % (
            biden_vote_decrease_total,
            biden_vote_decrease_times,
            trump_vote_decrease_total,
            trump_vote_decrease_times,
        )
    )
