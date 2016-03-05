from flask import *
import json
import urllib2
from random import randint
from user import User
from group import Group
from userLocation import UserLocation

app = Flask(__name__)
tokenToUserMap = {}
tokenToGroupMap = {}
groupToUserListMap = {} 		#[groupId] -> [list of users]
groupIdToUserLocationMap = {}	# saves the pending requests

@app.route('/register',methods=['POST'])
def registerApp():
	data = json.loads(request.data)
	print data
	gcmToken = data['gcmToken']
	groupId = data['groupId']
	username = data['username']
	user = User(gcmToken, groupId, username)
	tokenToUserMap[gcmToken] = user
	groupToUserListMap[groupId].append(user)
	print groupToUserListMap
	print tokenToUserMap
	return "OK"

@app.route('/sendLocation',methods=['POST'])
def sendLocation():
	data = json.loads(request.data)
	print data
	latitude = data['latitude']
	longitude = data['longitude']
	gcmToken = data['gcmToken']
	for groupId in groupIdToUserLocationMap:
		users = groupIdToUserLocationMap[groupId]
		if gcmToken in users:
			users[gcmToken].lat = latitude
			users[gcmToken].lon = longitude
	print groupIdToUserLocationMap
	return "OK"

def initiateMeeting(groupId):
	if groupId in groupIdToUserLocationMap:
		return
	users = groupToUserListMap[groupId]
	# sendToGcm(users)
	groupIdToUserLocationMap[groupId] = {}
	for user in users:
		print user
		userLoc = UserLocation(user.gcmToken)
		print userLoc
		groupIdToUserLocationMap[groupId][user.gcmToken] = userLoc
	print groupIdToUserLocationMap

@app.route('/flockToServer',methods=['POST'])
def flockToUs():
	data = json.loads(request.data)
	print data
	token = request.args.get('token')
	text = data['text']

	if text.startswith("#register"):
		arr = text.split()
		tokenToGroupMap[token] = Group(token, arr[1])
		if not token in groupToUserListMap:
			groupToUserListMap[token] = []
		return getFlockResponse("inout://groupId=" + token)
	elif text.startswith("#getLink"):
		return getFlockResponse("inout://groupId=" + token)
	elif text.startswith("#meeting"):
		initiateMeeting(token)
		return getFlockResponse("initiating a meeting")
	return "OK"

def getFlockResponse(message):
	postData = "{\"text\" : " + "\"" + message + "\"}"
	print postData
	return postData

# def sendToFlock(message, convData):
# 	data = {
# 		"text": messagePrefix + message
# 	}

# 	req = urllib2.Request(convData.assignedPerson.webhookUrl)
# 	req.add_header('Content-Type', 'application/json')
# 	response = urllib2.urlopen(req, json.dumps(data))

def sendToGcm(users):
	gcmTokenList = []
	for user in users:
		gcmTokenList.append(user.gcmToken)

	req = urllib2.Request("http://www.dhiwal.com:9003/sendMessage")   #gcm server url
	req.add_header('Content-Type', 'application/json')
	response = urllib2.urlopen(req, json.dumps(gcmTokenList))

@app.after_request
def apply_headers(response):
	response.headers["Content-Type"] = "application/json"
	return response


if __name__ == '__main__':
	app.run(host= '0.0.0.0', port=8090, debug=True)
















