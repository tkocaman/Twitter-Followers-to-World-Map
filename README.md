# Get Twitter followers and show their locations on the map.

## Installation and preparation

This project runs on Python 3.8+ 
There are some general library requirements for the project
- pandas==1.2.4
- Flask==2.0.0
- geopy==2.1.0
- tweepy==3.10.0

Install all the packages from the requirements.txt file.
```bash
pip install -r requirements.txt
```
To start you need to create a consumer key and secret, and an access key and secret. Go to http://dev.twitter.com, log on and go to the apps tab. Once you have those four values put them to "twitter_auth_data.json" file.

## What's in the repo

| File | Usage |
| ------ | ------ |
|/source | contains script files.|
|/data | contains data files used and produced by the scripts|
|requirements.txt | file for installing dependencies via pip|
|main.py | file for getting followers via Tweepy and getting user locations via geopy saving them into two seperate files inside data folder.|
|app.py | runs flask app.|
|dictionaries.py | Includes dictionary for mapping geo-locations.|
|index.html | flask template for rendering.|
|twitter_auth_data.json | keeps your twitter API credentals.|
|follower_list.csv | Twitter folllowers stores in.|
|location_data.json | includes data for Highcharts Map|

## Usage
**1**- To get the followers list
```bash
python main.py <username>
```
Example: 
```bash
python main.py POTUS
```
**2**- Run flask webpage
```bash
python app.py
```
**ENJOY :)**
