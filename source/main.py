import os
import sys
import json
import time
import tweepy
import pandas as pd
import dictionaries
import warnings
import datetime
import traceback

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


class TweetToMap(object):
    # connect twitter api

    HOME_PATH = os.path.dirname(__file__)

    twitter_auth_data = open(os.path.abspath(os.path.join(HOME_PATH, "..", "twitter_auth_data.json"))).read()
    twitter_auth_data_json = json.loads(twitter_auth_data)

    access_token = twitter_auth_data_json["access_token"]
    access_token_secret = twitter_auth_data_json["access_token_secret"]
    consumer_key = twitter_auth_data_json["consumer_key"]
    consumer_secret = twitter_auth_data_json["consumer_secret"]

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    def __init__(self, screen_name):

        self.screen_name = screen_name
        self.api = tweepy.API(TweetToMap.auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, retry_count=10, retry_delay=5, retry_errors=set([503]))
        self.follower_list_csv = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "follower_list.csv"))
        self.location_data_json = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "location_data.json"))

    def get_followers_list(self):
        # Source code of this function is from : https://stackoverflow.com/a/58234314
        follower_ids = []
        for user in tweepy.Cursor(self.api.followers_ids, screen_name=self.screen_name, count=5000).items():
            follower_ids.append(user)

        follower_list = []
        u_count = len(follower_ids)

        try:
            for i in range(int(u_count / 100) + 1):
                end_loc = min((i + 1) * 100, u_count)
                listf = self.api.lookup_users(user_ids=follower_ids[i * 100 : end_loc])

                batch_list = []
                for user in listf:
                    data = {
                        "id": user.id,
                        "name": user.name,
                        "screen_name": user.screen_name,
                        "location": user.location,
                        "description": user.description.replace("\n", " ").replace("\r", " ").replace("\n\r", " "),
                        "followers_count": user.followers_count,
                        "friends_count": user.friends_count,
                        "verified": user.verified,
                        "profile_image_url": user.profile_image_url,
                    }
                    batch_list.append(data)

                follower_list.extend(batch_list)
                print(f"{i}/{int(u_count/100) + 1}")

        except:
            traceback.print_exc()
            print(f"Something went wrong, quitting... i is {i}")

        follower_list = pd.DataFrame.from_dict(follower_list)
        follower_list.to_csv(self.follower_list_csv, index=False)

    def follower_loc_to_map(self):
        # remove warnings
        warnings.filterwarnings("ignore", "This pattern has match groups")
        pd.options.mode.chained_assignment = None  # default='warn'
        #
        followers = pd.read_csv(self.follower_list_csv)
        locations = followers["location"]
        locations.dropna(inplace=True)

        # Mapping followers' locations to Countries before sending geocoding services
        for k, v in dictionaries.majorUScities.items():
            mask = locations.str.contains(k, case=False)
            locations.loc[mask] = v

        for k, v in dictionaries.abbrevToSname.items():
            mask = locations.str.contains(k, case=True)
            locations.loc[mask] = v

        for k, v in dictionaries.countries.items():
            pat = "|".join(v)
            mask = locations.str.contains(pat, case=False)
            locations.loc[mask] = k

        for k, v in dictionaries.flags.items():
            mask = locations.str.contains(k, case=False)
            locations.loc[mask] = v

        for k, v in dictionaries.fineTuneMap.items():
            mask = locations.str.match(k, case=False)
            locations.loc[mask] = v

        locations = locations[~locations.str.contains("|".join(dictionaries.deleteContains), case=False)]
        locations = locations[~locations.str.contains("\d")]
        locations = locations[~locations.str.contains(r"[0-9]")]

        # Value Count
        locTogeo = locations.value_counts().rename_axis("unique_values").reset_index(name="counts")

        # To geocoding
        TweetToMap(self.screen_name).geocoding(locTogeo)

    def geocoding(self, locTogeo):
        ### obtain geolocations from nominatim service
        locTogeo["lat"] = 0
        locTogeo["long"] = 0
        locTogeo["country"] = "none"
        locTogeo["code"] = "none"

        print(f"This proccess will take about {len(locTogeo)}seconds or {len(locTogeo)/60} min")

        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        finish_time = now + datetime.timedelta(minutes=len(locTogeo) / 60)
        finish_time = finish_time.strftime("%H:%M:%S")
        print(f"Started at : {current_time}")
        print(f"Finish time is: ~ {finish_time}")

        for i, row in locTogeo.iterrows():
            geolocator = Nominatim(user_agent="twitter-analysis")

            try:
                location = geolocator.geocode(row["unique_values"], language="en")
                locTogeo.loc[i, "lat"] = location.latitude
                locTogeo.loc[i, "long"] = location.longitude
                locTogeo.loc[i, "country"] = location.raw["display_name"]
            except AttributeError:
                locTogeo.loc[i, "lat"] = "none"
                locTogeo.loc[i, "long"] = "none"
                locTogeo.loc[i, "country"] = "none"
            except GeocoderTimedOut:
                locTogeo.loc[i, "lat"] = "none"
                locTogeo.loc[i, "long"] = "none"
                locTogeo.loc[i, "country"] = "none"
            except GeocoderUnavailable:
                locTogeo.loc[i, "lat"] = "none"
                locTogeo.loc[i, "long"] = "none"
                locTogeo.loc[i, "country"] = "none"
            time.sleep(1)

        # Save data to a json file for Highcharts
        TweetToMap(self.screen_name).geocode_to_json(locTogeo)

    def geocode_to_json(self, locTogeo):
        locTogeo = locTogeo[~locTogeo["country"].str.contains("none")]

        # Some US states are also country names. Fix that issue.
        locTogeo.loc[(locTogeo["country"].str.contains("Georgia") & locTogeo["country"].str.contains("United States")), "code"] = "us-ga"
        locTogeo.loc[(locTogeo["country"].str.contains("Mexico") & locTogeo["country"].str.contains("United States")), "code"] = "us-nm"
        locTogeo.loc[(locTogeo["country"].str.contains("Indiana") & locTogeo["country"].str.contains("United States")), "code"] = "us-in"

        locTogeo.loc[locTogeo["country"] == "United States", "code"] = "us"

        for k, v in dictionaries.state_to_mapcode.items():
            mask = locTogeo["country"].str.contains(k, case=True)
            locTogeo.loc[mask, "code"] = v

        f = lambda x: x["country"].split(",")[-1]
        locTogeo["country"] = locTogeo.apply(f, axis=1)

        locTogeo.loc[locTogeo["country"].str.contains("Nigeria"), "country"] = "Ng_country"
        locTogeo.loc[locTogeo["country"].str.contains("Bissau"), "country"] = "Bissau"
        locTogeo.loc[locTogeo["country"].str.contains("Papua"), "country"] = "Papua"
        locTogeo.loc[locTogeo["country"].str.contains("Equatorial"), "country"] = "Equatorial"
        locTogeo.loc[locTogeo["country"].str.contains("Brazzaville"), "country"] = "Brazzaville"

        for k, v in dictionaries.country_to_mapcode.items():
            mask = locTogeo["country"].str.contains(k, case=False)
            locTogeo.loc[mask, "code"] = v

        locTogeo = locTogeo.groupby(locTogeo["code"]).agg({"counts": "sum"}).reset_index()
        locTogeo.sort_values(by="counts", ascending=False)

        usTotalCount = locTogeo.loc[(locTogeo["code"] == "us") | (locTogeo["code"].str.contains("-")), "counts"].sum()
        locTogeo.loc[locTogeo["code"] == "us", "counts"] = usTotalCount

        dataUs = locTogeo[locTogeo["code"].str.contains("-")].values.tolist()
        dataWorld = locTogeo.values.tolist()

        json_data = {
            "dataWorld": dataWorld,
            "dataUs": dataUs,
        }
        with open(self.location_data_json, "w") as fp:
            json.dump(json_data, fp, sort_keys=True)


if __name__ == "__main__":
    username = sys.argv[1]
    TweetToMap(username).get_followers_list()
    TweetToMap(username).follower_loc_to_map()
