#!/usr/bin/env python
# This script translates English words into Chinese line by line in an file
# It scrapes Google translate page to get around paying for Google API

import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import sys
import time
from xvfbwrapper import Xvfb

# Custom EC for WebDriverWait
class text_to_be_changed(object):
	def __init__(self, locator, text):
		self.locator = locator
		self.text = text

	def __call__(self, driver):
		return driver.find_element(*self.locator).text != self.text

# Get filename from command line argument
if len(sys.argv) < 2:
	print "Filename not provided!"
	sys.exit(1)
inFname = sys.argv[1]
outFname = "zh_" + inFname

# Read input file with English words, one word per line
with open(inFname, "r") as fIn:
	enWords = fIn.readlines()
# Remove trailing empty lines and trim white spaces in other lines
i = len(enWords) - 1
while i >= 0:
	enWords[i] = enWords[i].strip()
	if i == len(enWords) - 1 and enWords[i] == "":
		enWords.pop()
	i -= 1
print("Starting to translate %d words..." % len(enWords))

# Scrape Google translate page to perform translation
display = Xvfb()
display.start()
browser = webdriver.Chrome()
browser.implicitly_wait(10)
browser.get("https://translate.google.com/#en/zh-CN")
inBox = browser.find_element_by_xpath("//*[@id='source']")
startTime = time.time()
with open(outFname, "w") as fOut:
	zhWord = ""
	i = 0
	while i < len(enWords):
		if enWords[i] == "":
			# Keep empty lines between words in output in order to align with input
			fOut.write("\n")
			i += 1
		else:
			try:
				# Refill input box and wait till output box's text is changed
				inBox.clear()
				inBox.send_keys(enWords[i])
				try:
					WebDriverWait(browser, 10).until(text_to_be_changed((By.XPATH, "//*[@id='result_box']/span"), zhWord))
				except:
					# It happens that two successive words have the identical translation
					# In that case, wait for 10 seconds then proceed
					pass
				zhWord = browser.find_element_by_xpath("//*[@id='result_box']/span").text
				fOut.write(zhWord.encode("utf8")+"\n")
				i += 1
			except:
				# On error occurrence, refresh page and no increment to i
				browser.refresh()
				inBox = browser.find_element_by_xpath("//*[@id='source']")
		remainingTime = str(datetime.timedelta(seconds=(time.time()-startTime)*(len(enWords)-i)/i)).split(".")[0]
		sys.stdout.write("\rProgress: %d/%d %s" % (i, len(enWords), remainingTime))
		sys.stdout.flush()
browser.quit()
display.stop()
print("Completed! Find results in file %s" % outFname)
