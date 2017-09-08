#!/usr/bin/env python
# This script fetches my 3 credit scores from KreditKarma and SelfLender
# TODO: Add proper error handling if it's to be shared
# TODO: Get Equifax Score.
# On CreditKarma, scores are rendered by as-yet-unknown JS, not found in page source. May have to use webdriver.

import re
import requests
import sys
from fake_useragent import UserAgent

# Get password from command line argument
if len(sys.argv) < 2 or len(sys.argv[1]) < 8:
	print "Password not provided or too short. Note that some special characters need to be escaped in cli."
	sys.exit(1)
password = sys.argv[1]

# Get TransUnion and Equifax Scores from CreditKarma
session = requests.Session()

resp = session.get("https://www.creditkarma.com/auth/logon")
stk = resp.text.encode("ascii", "ignore").split("name=\"stk\" value=\"")[1].split("\"")[0]
credential = {
	"username": "eamin.zhang@gmail.com",
	"password": password,
	"rememberEmail": "1",
	"stk": stk
}

session.post("https://www.creditkarma.com/auth/logon", data=credential)
resp = session.get("https://www.creditkarma.com/tools/credit-score-simulator")
if "score-value\" >" in resp.text:
	transunion = resp.text.encode("ascii", "ignore").split("score-value\" >")[1][:3]
	print "TransUnion:", transunion 
else:
	print "Failed to get TransUnion Score from CreditKarma"

# Get Experian Score from SelfLender
session = requests.Session()
headers = {"Referer": "https://www.selflender.com/", "User-Agent": str(UserAgent().chrome)}

resp = session.get("https://www.selflender.com/login", headers=headers)
token = resp.cookies["_csrf_token"]
credential = {
	"email": "eamin.zhang@gmail.com",
	"password": password,
	"_csrf_token": token
}

session.post("https://www.selflender.com/login", data=credential, headers=headers)
resp = session.get("https://www.selflender.com/home/dashboard", headers=headers)
if "myCreditScore = " in resp.text:
	experian = resp.text.encode("ascii", "ignore").split("myCreditScore = ")[1][:3]
	print "Experian:", experian
else:
	print "Failed to get Experian Score from SelfLender"
