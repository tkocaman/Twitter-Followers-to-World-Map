# Twitter-Followers-to-world-Map
Installation and preparation.


This project runs on Python 3.8+ 

There are some general library requirements for the project.

pandas==1.2.4
Flask==2.0.0
geopy==2.1.0
tweepy==3.10.0

Install all the packages from the requirements.txt file.

pip install -r requirements.txt

To start, you need to create a "consumer key," "secret," and an "access key," and "secret." Go to http://dev.twitter.com, log on and go to the Apps tab. Once you have those four values, put them in the "twitter_auth_data.json" file.




What's in the repo

/source - contains script files.
/data - contains data files used and produced by the scripts

requirements.txt - file for installing dependencies via pip
main.py - file for getting followers via Tweepy and getting user locations via geopy saving them into two separate files inside the data folder.
app.py - runs flask app.
dictionaries.py - Includes dictionary for mapping geo-locations.
index.html - flask template for rendering.
twitter_auth_data.json - keeps your Twitter API credentials.
follower_list.csv - Twitter followers stores inside.
location_data.json - includes data for Highcharts Map


Usage

1- To get the followers list

python main.py <username>

Example: 

python main.py POTUS

2- To see the map, run the flask webpage

python app.py
ENJOY :)


