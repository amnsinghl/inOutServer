from flask import *
import json
import urllib2
from random import randint
from threading import Timer
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
	latitude = float(data['latitude'])
	longitude = float(data['longitude'])
	gcmToken = data['gcmToken']
	for groupId in groupIdToUserLocationMap:
		users = groupIdToUserLocationMap[groupId]
		if gcmToken in users:
			users[gcmToken].lat = latitude
			users[gcmToken].lon = longitude
			users[gcmToken].locationSet = True
	print groupIdToUserLocationMap
	return "OK"

def initiateMeeting(groupId):
	if groupId in groupIdToUserLocationMap:
		return
	users = groupToUserListMap[groupId]
	sendToGcm(users)
	groupIdToUserLocationMap[groupId] = {}
	for user in users:
		print user
		userLoc = UserLocation(user.gcmToken)
		print userLoc
		groupIdToUserLocationMap[groupId][user.gcmToken] = userLoc
	print groupIdToUserLocationMap
	t = Timer(30.0, sendMemberStatusToFlock,[groupId])
	t.start() # after 30 seconds, "hello, world" will be printed

import math
 
def distance(lat1, long1, lat2, long2):
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
    # Compute spherical distance from spherical coordinates.
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
    return arc * 6371000

def isAtWork(userLoc):
	wlat = 28.4567591
	wlon = 77.0658416
	dis = distance(wlat, wlon, userLoc.lat, userLoc.lon)
	print dis
	if abs(dis) < 300:
		return True
	return False

def sendMemberStatusToFlock(groupId):
	avail = []
	unavail = []
	cantsay = []
	userLocMap = groupIdToUserLocationMap[groupId]
	for token in userLocMap:
		username = tokenToUserMap[token].username
		if userLocMap[token].locationSet:
			if isAtWork(userLocMap[token]):
				avail.append(username)
			else:
				unavail.append(username)
		else:
			cantsay.append(username)
	groupIdToUserLocationMap.pop(groupId)
	ret = "Available: "
	for st in avail:
		ret += st + ", "
	ret += "\nUnavailable: "
	for st in unavail:
		ret += st + ", "
	ret += "\nCan't say: "
	for st in cantsay:
		ret += st + ", "
	print ret
	sendToFlock(ret, tokenToGroupMap[groupId].webhookUrl)

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

def sendToFlock(message, webhookUrl):
	data = {
		"text": messagePrefix + message
	}

	req = urllib2.Request(webhookUrl)
	req.add_header('Content-Type', 'application/json')
	response = urllib2.urlopen(req, json.dumps(data))

def sendToGcm(users):
	gcmTokenList = []
	for user in users:
		gcmTokenList.append(user.gcmToken)

	data = {
		"registrationId" : gcmTokenList
	}
	req = urllib2.Request("http://www.dhiwal.com:9003/sendToDevices")   #gcm server url
	req.add_header('Content-Type', 'application/json')
	response = urllib2.urlopen(req, json.dumps(data))

@app.after_request
def apply_headers(response):
	response.headers["Content-Type"] = "application/json"
	return response


if __name__ == '__main__':
	app.run(host= '0.0.0.0', port=8090, debug=True)


