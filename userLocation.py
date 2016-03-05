class UserLocation(object):
	gcmToken = ""
	lat = 0.0
	lon = 0.0
	
	def __init__(self, gcmToken):
		self.gcmToken = gcmToken

	def __repr__(self):
		return "gcmToken: " + self.gcmToken + "," + " lat: " + str(self.lat) +"," + " lon: " + str(self.lon);
