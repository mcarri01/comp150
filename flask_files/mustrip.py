import os
from flask import Flask
from geopy.geocoders import Nominatim
import json
from flask import request
from pymongo import MongoClient
from haversine import haversine

app = Flask(__name__)

@app.route('/')
def index():
	return "Welcome"

#TODO implement getting playlist by both city as well
@app.route("/playlistbycity", methods=['POST'])
def get_by_city():
	city = request.form["city"]
	geolocator = Nominatim()
	location = geolocator.geocode(city)
	lat = location.latitude
	lng = location.longitude
	my_coord = (float(lat), float(lng))
	return retrieve_playlist(my_coord)


@app.route("/getPlaylist", methods=['POST'])
def get_by_coord():
	mylat = request.form["lat"]
	mylng = request.form["lng"]
	my_coord = (float(mylat), float(mylng))
	return retrieve_playlist(my_coord)

def retrieve_playlist(my_coord):
	
	MONGODB_URI = "mongodb://mcarring:Keeker95@ds053156.mlab.com:53156/heroku_6132kr9d"
	client = MongoClient(MONGODB_URI)
	db = client.get_default_database()
	collection = db.cityData
	city_list = collection.find()
	# max distance between 2 points on earth
	min_distance = 20036
	city_playlist = 0
	city_name = ""
	for city in city_list:
		city_coord = (float(city.get('lat')), float(city.get('lng')))
		distance = haversine(my_coord, city_coord)
		if min_distance > distance:
			min_distance = distance
			city_playlist = city.get('distinctive_music')
			city_name = city.get('city')

	base_uri = "https://api.spotify.com/v1/users/thesoundsofspotify/playlists/"
	search_string = "/playlist/"
	# Get index of ID
	playlist_index = city_playlist.index(search_string)
	playlist_id = city_playlist[playlist_index + len(search_string):]
	# Return the playlist ID in URI form
	data = {}	
	data['city'] = city_name
	data['playlist'] = base_uri + playlist_id
	json_data = json.dumps(data)
	return json_data

if __name__ == "__main__":

	port = int(os.environ.get('PORT', 5000))
    	app.run(host='0.0.0.0', port=port)

