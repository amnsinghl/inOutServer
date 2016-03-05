class Group(object):
	token = ""
	webhookUrl = ""
	
	def __init__(self, token ,webhookUrl):
		self.token = token
		self.webhookUrl = webhookUrl

	def __repr__(self):
		return "token: " + self.token + "," + " webhook: " + self.webhookUrl;
