class User(object):
	gcmToken = ""
	groupId = ""
	username = ""
	
	def __init__(self, gcmToken ,groupId, username):
		self.gcmToken = gcmToken
		self.groupId = groupId
		self.username = username

	def __repr__(self):
		return "gcmToken: " + self.gcmToken + "," + " groupId: " + self.groupId;
