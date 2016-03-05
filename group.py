class Group(object):
	token = ""
	webhook = ""
	
	def __init__(self, token ,webhook):
		self.token = token
		self.webhook = webhook

	def __repr__(self):
		return "token: " + self.token + "," + " webhook: " + self.webhook;
