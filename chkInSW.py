#!/usr/bin/env python

import datetime
import pytz
import re
import requests
from selenium import webdriver
import sys
import time
from xvfbwrapper import Xvfb

# TODO: getopt -c -f -l

# Map from airport code to time zone
tzMap = requests.get("https://raw.githubusercontent.com/hroptatyr/dateutils/tzmaps/iata.tzmap").content

display = Xvfb()
display.start()
browser = webdriver.Chrome()

browser.get("https://www.southwest.com/air/manage-reservation/view.html?confirmationNumber=JX7ME6&passengerFirstName=Chi&passengerLastName=Zhang")
browser.implicitly_wait(1)
resvText = browser.execute_script("return document.body.innerText").encode("ascii", "ignore")

deptInfo = re.search(r"\nDeparting (\d+/\d+/\d+ [a-zA-Z]+day)\nDEPARTS(\d+:\d+[AP]M)([A-Z]{3})\n", resvText)
if deptInfo == None or len(deptInfo.groups()) != 3:
	print "Failed to retrieve departing flight information"
	sys.exit(1)
deptLocalTime = deptInfo.group(1) + " " + deptInfo.group(2)
deptAirport = deptInfo.group(3)
tzMatch = re.search(re.escape(deptAirport) + r"\t([A-Za-z/_]+)", tzMap)
if tzMatch == None:
	print "Airport %s is not found in timezone map" % deptAirport
	sys.exit(1)
deptTimezone = tzMatch.group(1)
deptUTCTime = pytz.timezone(deptTimezone).localize(datetime.datetime.strptime(deptLocalTime, "%m/%d/%y %A %I:%M%p"))

rtnInfo = re.search(r"\nReturning (\d+/\d+/\d+ [a-zA-Z]+day)\nDEPARTS(\d+:\d+[AP]M)([A-Z]{3})\n", resvText)
if rtnInfo == None or len(rtnInfo.groups()) != 3:
	print "Failed to retrieve returning flight information"
	sys.exit(1)
rtnLocalTime = rtnInfo.group(1) + " " + rtnInfo.group(2)
rtnAirport = rtnInfo.group(3)
tzMatch = re.search(re.escape(rtnAirport) + r"\t([A-Za-z/_]+)", tzMap)
if tzMatch == None:
	print "Airport %s is not found in timezone map" % rtnAirport
	sys.exit(1)
rtnTimezone = tzMatch.group(1)
rtnUTCTime = pytz.timezone(rtnTimezone).localize(datetime.datetime.strptime(rtnLocalTime, "%m/%d/%y %A %I:%M%p"))

browser.quit()
display.stop()

print "Departing from %s\n%s: %s\nUTC: %s\n" % (deptAirport, deptTimezone, deptLocalTime, deptUTCTime.astimezone(pytz.utc).strftime("%m/%d/%Y %H:%M"))
print "Returning from %s\n%s: %s\nUTC: %s\n" % (rtnAirport, rtnTimezone, rtnLocalTime, rtnUTCTime.astimezone(pytz.utc).strftime("%m/%d/%Y %H:%M"))

secBeforeChkIn = (deptUTCTime - datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1, minutes=1)).total_seconds()
if secBeforeChkIn >= 0:
	print "Sleeping %d seconds before attempting to check in\n" % secBeforeChkIn
	time.sleep(secBeforeChkIn)

# TODO: https://www.southwest.com/air/check-in/index.html?confirmationNumber=JX7ME6&passengerFirstName=Chi&passengerLastName=Zhang
# browser.find_element_by_id("form-mixin--submit-button").click()
