#!/usr/bin/env python

import datetime
import pytz
import re
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import sys
import time
from xvfbwrapper import Xvfb

# TODO: getopt -c -f -l -m
confirmationNumber = "WIT2OC"
firstName = "Chi"
lastName = "Zhang"
mobileNumber = "5713093797"

def checkIn():
	display = Xvfb()
	display.start()
	browser = webdriver.Chrome()
	browser.implicitly_wait(1)

	browser.get("https://www.southwest.com/air/check-in/index.html?confirmationNumber=%s&passengerFirstName=%s&passengerLastName=%s"
		 % (confirmationNumber, firstName, lastName))
	while True:
		try:
			browser.find_element_by_id("form-mixin--submit-button").click()
			WebDriverWait(browser, 5).until(EC.element_to_be_clickable((By.XPATH, "//*[@id='swa-content']/div/div[2]/div/section/div/div/div[3]/button")))
			break
		except:
			browser.refresh()
	browser.find_element_by_xpath("//*[@id='swa-content']/div/div[2]/div/section/div/div/div[3]/button").click()
	browser.find_element_by_xpath("//*[@id='swa-content']/div/div[2]/div/section/div/div/section/table/tbody/tr/td[3]/button").click()
	browser.find_element_by_id("textBoardingPass").send_keys(mobileNumber)
	browser.find_element_by_id("form-mixin--submit-button").click()

	browser.quit()
	display.stop()

# Map from airport code to time zone
tzMap = requests.get("https://raw.githubusercontent.com/hroptatyr/dateutils/tzmaps/iata.tzmap").content

# TODO: functionize the following code
display = Xvfb()
display.start()
browser = webdriver.Chrome()
browser.implicitly_wait(1)

browser.get("https://www.southwest.com/air/manage-reservation/view.html?confirmationNumber=%s&passengerFirstName=%s&passengerLastName=%s"
	% (confirmationNumber, firstName, lastName))
WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.ID, "heading-20")))
resvText = browser.execute_script("return document.body.innerText").encode("ascii", "ignore")

deptInfo = re.search(r"\nDeparting (\d+/\d+/\d+ [a-zA-Z]+day)\nDEPARTS(\d+:\d+[AP]M)([A-Z]{3})\n", resvText)
if deptInfo == None or len(deptInfo.groups()) != 3:
	print "Failed to retrieve departing flight information\n"
else:
	deptLocalTime = deptInfo.group(1) + " " + deptInfo.group(2)
	deptAirport = deptInfo.group(3)
	tzMatch = re.search(re.escape(deptAirport) + r"\t([A-Za-z/_]+)", tzMap)
	if tzMatch == None:
		print "Airport %s is not found in timezone map\n" % deptAirport
		sys.exit(1)
	deptTimezone = tzMatch.group(1)
	deptUTCTime = pytz.timezone(deptTimezone).localize(datetime.datetime.strptime(deptLocalTime, "%m/%d/%y %A %I:%M%p"))
	print "Departing from %s\n%s: %s\nUTC: %s\n" % (deptAirport, deptTimezone, deptLocalTime, deptUTCTime.astimezone(pytz.utc).strftime("%m/%d/%Y %H:%M"))

rtnInfo = re.search(r"\nReturning (\d+/\d+/\d+ [a-zA-Z]+day)\nDEPARTS(\d+:\d+[AP]M)([A-Z]{3})\n", resvText)
if rtnInfo == None or len(rtnInfo.groups()) != 3:
	print "Failed to retrieve returning flight information\n"
else:
	rtnLocalTime = rtnInfo.group(1) + " " + rtnInfo.group(2)
	rtnAirport = rtnInfo.group(3)
	tzMatch = re.search(re.escape(rtnAirport) + r"\t([A-Za-z/_]+)", tzMap)
	if tzMatch == None:
		print "Airport %s is not found in timezone map\n" % rtnAirport
		sys.exit(1)
	rtnTimezone = tzMatch.group(1)
	rtnUTCTime = pytz.timezone(rtnTimezone).localize(datetime.datetime.strptime(rtnLocalTime, "%m/%d/%y %A %I:%M%p"))
	print "Returning from %s\n%s: %s\nUTC: %s\n" % (rtnAirport, rtnTimezone, rtnLocalTime, rtnUTCTime.astimezone(pytz.utc).strftime("%m/%d/%Y %H:%M"))

browser.quit()
display.stop()

try:
	deptUTCTime
except:
	pass
else:
	if datetime.datetime.now(pytz.utc) > deptUTCTime:
		print "Departing flight has already left\n"
	else:
		secBeforeChkIn = (deptUTCTime - datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1, minutes=1)).total_seconds()
		if secBeforeChkIn > 0:
			print "Sleeping %d seconds before attempting to check in departing flight\n" % secBeforeChkIn
			time.sleep(secBeforeChkIn)
		checkIn()
		print "Checked in departing flight\n"

try:
	rtnUTCTime
except:
	pass
else:
	if datetime.datetime.now(pytz.utc) > rtnUTCTime:
		print "Returning flight has already left\n"
	else:
		secBeforeChkIn = (rtnUTCTime - datetime.datetime.now(pytz.utc) - datetime.timedelta(days=1, minutes=1)).total_seconds()
		if secBeforeChkIn > 0:
			print "Sleeping %d seconds before attempting to check in returning flight\n" % secBeforeChkIn
			time.sleep(secBeforeChkIn)
		checkIn()
		print "Checked in returning flight\n"
