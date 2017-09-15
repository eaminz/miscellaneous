#!/usr/bin/env python
# This script scrapes my 3 credit scores from KreditKarma and SelfLender

from fake_useragent import UserAgent
import requests
from selenium import webdriver
import sys
from xvfbwrapper import Xvfb

# Get password from command line argument
if len(sys.argv) < 2 or len(sys.argv[1]) < 8:
	print "Password not provided or too short. Note that some special characters need to be escaped in cli."
	sys.exit(1)
password = sys.argv[1]

print "Scraping my credit scores. This could take up to 20 seconds."

# Get TransUnion and Equifax Scores from CreditKarma using selenium webdriver
display = Xvfb()
display.start()
browser = webdriver.Chrome()
browser.get("https://www.creditkarma.com/auth/logon/")
browser.find_element_by_id("username").send_keys("eamin.zhang@gmail.com")
browser.find_element_by_id("password").send_keys(password)
browser.find_element_by_id("Logon").click()
browser.implicitly_wait(15)
try:
	print "TransUnion:", browser.find_element_by_xpath("//*[@id='__galaxy']/div/main/div[2]/div/div/div/section[1]/div[1]/a[1]") \
		.find_elements_by_tag_name("text")[6].text
except:
	print "Failed to get TransUnion Score from CreditKarma"
try:
	print "Equifax:", browser.find_element_by_xpath("//*[@id='__galaxy']/div/main/div[2]/div/div/div/section[1]/div[1]/a[2]") \
		.find_elements_by_tag_name("text")[6].text
except:
	print "Failed to get Equifax Score from CreditKarma"
browser.quit()
display.stop()

# Get Experian Score from SelfLender using requests session
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
	print "Experian:", resp.text.encode("ascii", "ignore").split("myCreditScore = ")[1][:3]
else:
	print "Failed to get Experian Score from SelfLender"
